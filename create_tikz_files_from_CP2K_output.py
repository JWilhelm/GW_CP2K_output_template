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


# Generate the atoms for the square pyramid
n_bands = get_number_of_bands("bandstructure_SCF.bs")
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
