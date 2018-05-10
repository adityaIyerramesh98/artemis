from glob import glob
import numpy as np
from collections import namedtuple

HeaderInfo = namedtuple('HeaderInfo', ['version', 'how', 'ncomp', 'nghost'])

_component_names = ['Ex', 'Ey', 'Ez', 'Bx', 'By', 'Bz', 'jx', 'jy', 'jz', 'rho']

def read_data(plt_file):
    '''

    This function reads the raw (i.e. not averaged to cell centers) data
    from a WarpX plt file. The plt file must have been written with the
    plot_raw_fields option turned on, so that it contains a raw_data
    sub-directory. This is only really useful for single-level data.

    Arguments:

        plt_file : An AMReX plt_file file. Must contain a raw_data directory.

    Returns:

        A list of dictionaries where the keys are field name strings and the values
        are numpy arrays. Each entry in the list corresponds to a different level.

    Example:

        >>> data = read_data("plt00016")
        >>> print(data.keys())
        >>> print(data['Ex'].shape)

    '''
    all_data = []
    raw_files = glob(plt_file + "/raw_fields/Level_*/")
    for raw_file in raw_files:
        field_names = _get_field_names(raw_file)

        data = {}
        for field in field_names:
            data[field] = _read_field(raw_file, field)

        all_data.append(data)

    return all_data


def read_lab_snapshot(snapshot):
    '''

    This reads the data from one of the lab frame snapshots generated when
    WarpX is run with boosted frame diagnostics turned on. It returns a
    dictionary of numpy arrays, where each key corresponds to one of the
    data fields ("Ex", "By,", etc... ). These values are cell-centered.

    '''

    hdrs = glob(snapshot + "/Level_0/buffer*_H")
    hdrs.sort()

    boxes, file_names, offsets, header = _read_header(hdrs[0])
    dom_lo, dom_hi = _combine_boxes(boxes)
    domain_size = dom_hi - dom_lo + 1

    space_dim = len(dom_lo)
    if space_dim == 2:
        direction = 1
    else:
        direction = 2

    buffer_data = _read_buffer(snapshot, hdrs[0])
    buffer_size = buffer_data['Bx'].shape[direction]

    data = {}
    for i in range(header.ncomp):
        if space_dim == 3:
            data[_component_names[i]] = np.zeros((domain_size[0], domain_size[1], buffer_size*len(hdrs)))
        elif space_dim == 2:
            data[_component_names[i]] = np.zeros((domain_size[0], buffer_size*len(hdrs)))

    for i, hdr in enumerate(hdrs):
        buffer_data = _read_buffer(snapshot, hdr)
        if data is None:
            data = buffer_data
        else:
            for k,v in buffer_data.items():
                if space_dim == 3:
                    data[k][:,:,buffer_size*i:buffer_size*(i+1)] = v[:,:,:]
                elif space_dim == 2:
                    data[k][:,buffer_size*i:buffer_size*(i+1)] = v[:,:]

    return data


def _get_field_names(raw_file):
    header_files = glob(raw_file + "*_H")
    return [hf.split("/")[-1][:-2] for hf in header_files]


def _string_to_numpy_array(s):
    return np.array([int(v) for v in s[1:-1].split(",")], dtype=np.int64)


def _line_to_numpy_arrays(line):
    lo_corner = _string_to_numpy_array(line[0][1:])
    hi_corner = _string_to_numpy_array(line[1][:])
    node_type = _string_to_numpy_array(line[2][:-1])
    return lo_corner, hi_corner, node_type


def _read_header(header_file):
    with open(header_file, "r") as f:

        version = int(f.readline())
        how = int(f.readline())
        ncomp = int(f.readline())
        nghost = int(f.readline())

        header = HeaderInfo(version, how, ncomp, nghost)

        # skip the next line
        f.readline()

        # read boxes
        boxes = []
        for line in f:
            clean_line = line.strip().split()
            if clean_line == [')']:
                break
            lo_corner, hi_corner, node_type = _line_to_numpy_arrays(clean_line)
            boxes.append((lo_corner - nghost,
                          hi_corner + nghost,
                          node_type))

        # read the file and offset position for the corresponding box
        file_names = []
        offsets = []
        for line in f:
            if line.startswith("FabOnDisk:"):
                clean_line = line.strip().split()
                file_names.append(clean_line[1])
                offsets.append(int(clean_line[2]))

    return boxes, file_names, offsets, header


def _combine_boxes(boxes):
    lo_corners, hi_corners = zip(*[(box[0], box[1]) for box in boxes])
    domain_lo = np.min(lo_corners, axis=0)
    domain_hi = np.max(hi_corners, axis=0)
    return domain_lo, domain_hi


def _read_field(raw_file, field_name):

    header_file = raw_file + field_name + "_H"
    boxes, file_names, offsets, header = _read_header(header_file)

    ng = header.nghost
    dom_lo, dom_hi = _combine_boxes(boxes)
    data = np.zeros(dom_hi - dom_lo + 1)

    for box, fn, offset in zip(boxes, file_names, offsets):
        lo = box[0] - dom_lo
        hi = box[1] - dom_lo
        shape = hi - lo + 1
        with open(raw_file + fn, "rb") as f:
            f.seek(offset)
#            f.readline()  # always skip the first line
            arr = np.fromfile(f, 'float64', np.product(shape))
            arr = arr.reshape(shape, order='F')
            data[[slice(l,h+1) for l, h in zip(lo, hi)]] = arr

    return data



def _read_buffer(snapshot, header_fn):

    boxes, file_names, offsets, header = _read_header(header_fn)

    ng = header.nghost
    dom_lo, dom_hi = _combine_boxes(boxes)

    all_data = {}
    for i in range(header.ncomp):
        all_data[_component_names[i]] = np.zeros(dom_hi - dom_lo + 1)

    for box, fn, offset in zip(boxes, file_names, offsets):
        lo = box[0] - dom_lo
        hi = box[1] - dom_lo
        shape = hi - lo + 1
        size = np.product(shape)
        with open(snapshot + "/Level_0/" + fn, "rb") as f:
            f.seek(offset)
#            f.readline()  # always skip the first line
            arr = np.fromfile(f, 'float64', header.ncomp*size)
            for i in range(header.ncomp):
                comp_data = arr[i*size:(i+1)*size].reshape(shape, order='F')
                data = all_data[_component_names[i]]
                data[[slice(l,h+1) for l, h in zip(lo, hi)]] = comp_data
                all_data[_component_names[i]] = data
    return all_data


if __name__ == "__main__":
    data = read_lab_snapshot("lab_frame_data/snapshot00012");
