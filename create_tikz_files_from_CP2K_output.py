import os 

def create_directory_if_not_exists(directory_name):
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

def get_number_of_bands(filename):
    found = False
    prev_line = None
    target = "# Point 2"
    with open(filename, 'r') as file:
        for line in file:
            if target in line:
                found = True
                break
            prev_line = line

    line_split = prev_line.split()

    n_bands = int(line_split[0])

    return n_bands

def get_number_of_kpoints(filename):

    with open(filename, 'r') as file:
        first_line = file.readline().strip()

    line_split = first_line.split()

    nkp_special = int(line_split[1])
    nkp = int(line_split[4])

    return nkp, nkp_special

def any_number_in_interval(arr, a, b):
    for num in arr:
        if a <= num <= b:
            return True
    return False

def read_bandstructure_and_write_tikz_data(filename, fname_write, nkp, nkp_special, n_bands, e_fermi, energy_window):

    bandstructure = [[0.0] *  nkp for _ in range(n_bands)]
    xkp = [0.0] * nkp
    ykp = [0.0] * nkp
    zkp = [0.0] * nkp
    abskp = [0.0] * nkp
    ikp = 0
    with open(filename, 'r') as file:
        for line in file:

            line_split = line.split()

            if "#  Point" in line:
                xkp[ikp] = float(line_split[4])
                ykp[ikp] = float(line_split[5])
                zkp[ikp] = float(line_split[6])
                if ikp >= 1:
                  abskp[ikp] = abskp[ikp-1] + ((xkp[ikp]-xkp[ikp-1])**2 + \
                               (ykp[ikp]-ykp[ikp-1])**2 + (zkp[ikp]-zkp[ikp-1])**2)**0.5
                ikp+=1

            if "#" not in line: 
                band_index = int(line_split[0])
                band_energy = float(line_split[1])
                bandstructure[band_index-1][ikp-1] = band_energy

    for band_index in range(n_bands):
        e1 = e_fermi - energy_window/2
        e2 = e_fermi + energy_window/2
        is_band_around_e_fermi = any_number_in_interval(bandstructure[band_index], e1, e2)
        if is_band_around_e_fermi:
            with open(fname_write+str(band_index)+".dat", 'w') as f:
                for ikp in range(nkp):
                       f.write(str(abskp[ikp]) + ' ' + str(bandstructure[band_index][ikp]) + '\n')

# names and running the program
data_dir = "data"
bandstructure_file_cp2k = "bandstructure_SCF.bs"
create_directory_if_not_exists(data_dir)
nkp, nkp_special = get_number_of_kpoints(bandstructure_file_cp2k)
n_bands = get_number_of_bands(bandstructure_file_cp2k)
e_fermi = -1.0
energy_window = 10.0
read_bandstructure_and_write_tikz_data(bandstructure_file_cp2k, data_dir+"/band_SCF_", \
                                       nkp, nkp_special, n_bands, e_fermi, energy_window)
