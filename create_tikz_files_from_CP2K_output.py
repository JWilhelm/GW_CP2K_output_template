#def write_xyz_file(filename, atoms):
#    num_atoms = len(atoms)
#    with open(filename, 'w') as f:
#        f.write(str(num_atoms) + '\n')
#        f.write('Na atoms arranged in a square pyramid\n')
#        for atom in atoms:
#            f.write('Na {:.6f} {:.6f} {:.6f}\n'.format(*atom))

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

def read_bandstructure_and_write_tikz_data(filename, fname_write, nkp, nkp_special, n_bands):

    bandstructure = [[0.0] *  n_bands for _ in range(nkp)]
    xkp = [0.0] * nkp
    ykp = [0.0] * nkp
    zkp = [0.0] * nkp
    abskp = [0.0] * nkp
    ikp = 0
    with open(filename, 'r') as file:
        for line in file:

            line_split = line.split()

            if "# Point" in line:
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
                print("ikp", ikp)
                print("band_index", band_index)
                bandstructure[ikp][band_index-1] = band_energy


    for band_index in range(n_bands):
        with open(fname_write+str(band_index)+".dat", 'w') as f:
            for ikp in range(nkp):
               f.write(str(abskp[ikp]) + ' ' + str(bandstructure[ikp][band_index]) + '\n')


# Generate the atoms for the square pyramid
nkp, nkp_special = get_number_of_kpoints("bandstructure_SCF.bs")
n_bands = get_number_of_bands("bandstructure_SCF.bs")
read_bandstructure_and_write_tikz_data("bandstructure_SCF.bs", "band_SCF_", nkp, nkp_special, n_bands)
print("Number of kpoints is ", nkp)
print("Number of bands is ", n_bands)



## Write the atoms to an XYZ file
#filename = 'nat_'+str(len(atoms))+'_parameters_'+\
#str(n_vertical_double_layers_pyr)+'_'+\
#str(n_vertical_double_layers_cub)+'_'+\
#str(n_xy_cube)+'_'+\
#str(thickness_pyr )+'_'+\
#str(thickness_cub)+'_'+\
#str(dist_frontier_atoms)+\
#'.xyz'
#write_xyz_file(filename, atoms)
#
#print('XYZ file "{}" has been created.'.format(filename))
