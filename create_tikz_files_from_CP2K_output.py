import os 
import re

def clean_data_dir(data_dir):
    try:
        # Use os.rmdir to remove an empty directory
        os.rmdir(data_dir)
    except OSError:
        # If the directory is not empty, use os.remove for files and os.rmdir for directories recursively
        for root, dirs, files in os.walk(data_dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
        if os.path.exists(data_dir):
            os.rmdir(data_dir)

    os.mkdir(data_dir)


def find_single_file_with_patterns(patterns):
    matching_files = []

    for filename in os.listdir("."):
        file_path = os.path.join(".", filename)

        if os.path.isfile(file_path) and not filename.endswith(".matrix") and not filename.endswith(".py"):
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
            except Exception as e:
                continue  # Skip files that couldn't be read

            if all(re.search(pattern, content) for pattern in patterns):
                matching_files.append(filename)

    if len(matching_files) == 0:
        raise FileNotFoundError("No CP2K output file has been found.")
    elif len(matching_files) > 1:
        raise ValueError("Error: Multiple files matching all patterns found.")
    
    return matching_files[0]

def create_directory_if_not_exists(directory_name):
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

def get_nth_word(filename, n, pattern):
    with open(filename, 'r') as file:
        for line in file:
            if pattern in line:
                words = line.strip().split()  # Split the line into words
                if len(words) >= n:
                    tenth_word = words[n-1]  # Index 9 corresponds to the 10th word (0-based index)
                    return tenth_word  # Convert to integer

    return None 

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

def read_bandstructure_and_write_tikz_data(filename, scf_gw, fname_write, fname_commands, nkp, nkp_special, n_occ_bands, n_bands, energy_window, do_soc):

    bandstructure = [[0.0] *  nkp for _ in range(n_bands)]
    xkp = [0.0] * nkp
    ykp = [0.0] * nkp
    zkp = [0.0] * nkp
    abskp = [0.0] * nkp
    ikp = 0
    e_VBM = -1000
    e_CBM = 1000
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
                if band_index == n_occ_bands: 
                   e_VBM = max(e_VBM,bandstructure[band_index-1][ikp-1])
                if band_index == n_occ_bands+1:
                   e_CBM = min(e_CBM,bandstructure[band_index-1][ikp-1])

    e1 = e_VBM - energy_window/2
    e2 = e_CBM + energy_window/2

    with open(fname_commands, 'w') as f:
        f.write("\\newcommand{\\XMAXBS"+scf_gw+"}{"+str(abskp[-1])+"}\n")
        f.write("\\newcommand{\\YMINBS"+scf_gw+"}{"+str(-energy_window/2)+"}\n")
        f.write("\\newcommand{\\YMAXBS"+scf_gw+"}{"+str(e_CBM-e_VBM+energy_window/2)+"}\n")
        f.write("\\newcommand{\PLOTSBS"+scf_gw+"}{\n")

    for band_index in range(n_bands):
        is_band_around_e_fermi = any_number_in_interval(bandstructure[band_index], e1, e2)

        if is_band_around_e_fermi:
          fname_composed = fname_write+str(band_index)+".dat"
          with open(fname_composed, 'w') as f:
            for ikp in range(nkp):
              f.write(str(abskp[ikp]) + ' ' + str(bandstructure[band_index][ikp]-e_VBM) + '\n')
          with open(fname_commands, 'a') as f:
              if do_soc and band_index % 2 == 1:
                  f.write("\\addplot[very thick, orange, dashed, smooth] table {"+fname_composed+"};\n")
              else:
                  f.write("\\addplot[very thick, darkblue, smooth] table {"+fname_composed+"};\n")

    with open(fname_commands, 'a') as f:
        f.write("}\n")
        f.write("\\newcommand{\XTICKLABELS"+scf_gw+"}{xticklabels={")

    nkp_special = get_nth_word(filename, 2, "special points,")
    nkp_special = int(nkp_special)
    abskp = [0.0] * nkp_special
    xkp = [0.0] * nkp_special
    ykp = [0.0] * nkp_special
    zkp = [0.0] * nkp_special
    for ikp in range(nkp_special):
        if ikp != 0:
            with open(fname_commands, 'a') as f:
                f.write(", ")

        xkp_word = get_nth_word(filename, 5, "Special point "+str(ikp+1))
        ykp_word = get_nth_word(filename, 6, "Special point "+str(ikp+1))
        zkp_word = get_nth_word(filename, 7, "Special point "+str(ikp+1))
        kname = get_nth_word(filename, 8, "Special point "+str(ikp+1))

        xkp[ikp] = float(xkp_word)
        ykp[ikp] = float(ykp_word)
        zkp[ikp] = float(zkp_word)

        if ikp > 0:
           abskp[ikp] = ((xkp[ikp]-xkp[ikp-1])**2+(ykp[ikp]-ykp[ikp-1])**2+\
                         (zkp[ikp]-zkp[ikp-1])**2)**0.5 + abskp[ikp-1]

        if kname == "Gamma" or kname == "GAMMA":
            with open(fname_commands, 'a') as f:
                f.write("$\\Gamma$")
        else:
            with open(fname_commands, 'a') as f:
                f.write(kname)

    with open(fname_commands, 'a') as f:
        f.write("},}\n")
        f.write("\\newcommand{\TICKSSPECIALKPOINTSBS"+scf_gw+"}{")

    for ikp in range(nkp_special):
        if ikp != 0:
            with open(fname_commands, 'a') as f:
                f.write(", ")
        with open(fname_commands, 'a') as f:
            f.write(str(abskp[ikp]))

    with open(fname_commands, 'a') as f:
        f.write("}\n")


def read_dos_pdos_and_write_tikz_data(dos_pdos_file, scf_gw, data_dir, fname_commands):

    with open(dos_pdos_file, 'r') as file:
        for line in file:

            line_split = line.split()

            if "Energy" in line:
              n_atom_kind = len(line_split) - 9
              atom_kinds = line_split[9:]
              with open("DOS_"+scf_gw+"_commands.tex", 'w') as f:
                f.write("\\newcommand{\PLOTSDOS"+scf_gw+"}{\n")
                f.write("\\addplot[thick, darkblue, smooth] table[x index=1,y index=0] {data/DOS_"+scf_gw+".dat};\n")
                f.write("\\addlegendentry{DOS}")
                for kind in atom_kinds:
                  f.write("\\addplot[thick, smooth] table[x index=1,y index=0] {data/PDOS_"+scf_gw+"_"+kind+".dat};\n") 
                  f.write("\\addlegendentry{PDOS "+kind+"}")
                f.write("}\n")

            else:
              energy = line_split[0]
              dos = line_split[1]
              pdos = line_split[2:]

              with open(data_dir+"/DOS_"+scf_gw+".dat", 'a') as f:
                  f.write("     "+energy+" "+dos+"\n")

              for i_kind in range(n_atom_kind):
                  with open(data_dir+"/PDOS_"+scf_gw+"_"+atom_kinds[i_kind]+".dat", 'a') as f:
                     f.write("    "+energy+" "+pdos[i_kind]+"\n")



# names and running the program
data_dir = "data"
clean_data_dir(data_dir)

bandstructure_file_cp2k = "bandstructure_SCF.bs"
bandstructure_file_cp2k_soc = "bandstructure_SCF_SOC.bs"
bandstructure_file_cp2k_g0w0 = "bandstructure_G0W0.bs"
bandstructure_file_cp2k_g0w0_soc = "bandstructure_G0W0_SOC.bs"

dos_pdos_file_cp2k = "DOS_PDOS_SCF.out"
dos_pdos_file_cp2k_soc = "DOS_PDOS_SCF_SOC.out"
dos_pdos_file_cp2k_g0w0 = "DOS_PDOS_G0W0.out"
dos_pdos_file_cp2k_g0w0_soc = "DOS_PDOS_G0W0_SOC.out"

create_directory_if_not_exists(data_dir)
nkp, nkp_special = get_number_of_kpoints(bandstructure_file_cp2k)
n_bands = get_number_of_bands(bandstructure_file_cp2k)
cp2k_out_file_name = find_single_file_with_patterns(["GW CALC","time/freq. p","URE CALC"])
n_occ_bands = get_nth_word(cp2k_out_file_name, 10, "occupied bands in the primitive unit cell")
n_occ_bands = int(n_occ_bands)
n_vir_bands = get_nth_word(cp2k_out_file_name, 10, "unoccupied bands in the primitive unit cell")
n_vir_bands = int(n_vir_bands)
if n_occ_bands + n_vir_bands != n_bands:
  exit("error in number of bands")
energy_window = 7.0

read_bandstructure_and_write_tikz_data(bandstructure_file_cp2k, "SCF", data_dir+"/band_SCF_", \
                                       "bandstructure_SCF_commands.tex", nkp, nkp_special, \
                                       n_occ_bands, n_bands, energy_window, do_soc=False)
read_bandstructure_and_write_tikz_data(bandstructure_file_cp2k_soc, "SCFSOC", data_dir+"/band_SCF_SOC", \
                                       "bandstructure_SCF_SOC_commands.tex", nkp, nkp_special, \
                                       2*n_occ_bands, 2*n_bands, energy_window, do_soc=True)
read_bandstructure_and_write_tikz_data(bandstructure_file_cp2k_g0w0, "GW", data_dir+"/band_G0W0_", \
                                       "bandstructure_G0W0_commands.tex", nkp, nkp_special, \
                                       n_occ_bands, n_bands, energy_window, do_soc=False)
read_bandstructure_and_write_tikz_data(bandstructure_file_cp2k_g0w0_soc, "GWSOC", data_dir+"/band_SCF_G0W0_SOC", \
                                       "bandstructure_G0W0_SOC_commands.tex", nkp, nkp_special, \
                                       2*n_occ_bands, 2*n_bands, energy_window, do_soc=True)

read_dos_pdos_and_write_tikz_data(dos_pdos_file_cp2k, "SCF", data_dir, "DOS_SCF_commands.tex")
read_dos_pdos_and_write_tikz_data(dos_pdos_file_cp2k_g0w0, "GoWo", data_dir, "DOS_G0W0_commands.tex")
