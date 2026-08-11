import numpy as np


# Radial to horizontal and vertical
def rotating2cartesian(f_complex, phi, type='force'):
    f_abs = np.abs(f_complex)
    f_phase = np.angle(f_complex)
    phi_rad = np.deg2rad(phi)
    if type == 'moment':
        f_phase += np.pi / 2
    fy = -f_abs * np.sin(phi_rad + f_phase)  # Horizontal component
    fz = f_abs * np.cos(phi_rad + f_phase)  # Vertical component
    return fy, fz

# Projection to horizontal and vertical
def projection_yz(f, angle):
    angle_rad = np.deg2rad(angle)
    fy = -f * np.sin(angle_rad)  # Horizontal component
    fz = f * np.cos(angle_rad)  # Vertical component
    return fy, fz

# Complex to crank angle
def complex2crankangle(f_complex, harm_ord, phi):
    f_abs = np.abs(f_complex)[:, None]
    f_phase = np.angle(f_complex)[:, None]
    phi_rad = np.deg2rad(phi)[None, :]
    f_ca = f_abs * np.cos(harm_ord[:, None] * phi_rad + f_phase) #f(phi) = A * cos(n * phi + phase), n= harmonische ordnung, phi= Kurbelwinkel
    return f_ca

# Balancing forces
def mass_forces(eng_conf, crankshaft_geo, masses, throw_angles_mat, phi):

    # Engine configuration properties
    speed = eng_conf["speed"]
    n_cyl = eng_conf["n_cyl"] #Zylinderzahl
    cyl_arr = eng_conf["cyl_arr"] #Bauart
    vee = eng_conf["vee"]
    if cyl_arr == "In-line":
        raise ValueError("In-line configuration is not supported yet.")

    # Crankshaft geometry
    stroke = crankshaft_geo["stroke"]
    l_conrod = crankshaft_geo["l_conrod"]
    r_web = crankshaft_geo["r_web"]
    r_cw = crankshaft_geo["r_cw"]
    dist_main_main = crankshaft_geo["dist_main_main"]
    dist_main_cyl1 = crankshaft_geo["dist_main_cyl1"]
    dist_main_cyl2 = crankshaft_geo["dist_main_cyl2"]

    # Masses
    mass_piston = masses["mass_piston"]
    mass_con_se = masses["mass_con_se"]
    mass_con_be = masses["mass_con_be"]
    mass_pin = masses["mass_pin"]
    mass_web = masses["mass_web"]
    mass_cw = masses["mass_cw"]

    # Derived parameters
    if cyl_arr == "Vee":
        n_throw = n_cyl // 2 
        #für jeden Zylinder Bankwinkel (bei 50 ° Vee: 25 ° für Zylinder 1, -25 ° für Zylinder 2, usw.) 
        angle_bank = np.array([vee / 2 if i % 2 == 0 else -vee / 2 for _ in range(n_throw) for i in range(2)])
    else:
        n_throw = n_cyl
        angle_bank = np.zeros(n_cyl)
    omega = np.pi * speed / 30  # (rpm in rad/s)
    om2 = omega ** 2
    lam = stroke / 2 / l_conrod # r= stroke/2, lambda= r/l_conrod 
    mass_osc = mass_con_se + mass_piston #Kolben und kleines Pleuelende 
    
    # Vector with axial coordinate of each throw, and each cylinder
    x_throw = np.zeros(n_throw)
    for indt in range(n_throw):
        x_throw[indt] = -(indt * dist_main_main - ((n_throw - 1) / 2) * dist_main_main)
    x_cyl1 = x_throw + dist_main_main / 2 - dist_main_cyl1
    x_cyl2 = x_throw + dist_main_main / 2 - dist_main_cyl2
    x_cyl = [val for pair in zip(x_cyl1, x_cyl2) for val in pair]
    
    # Vector with oscillating forces (N)
    fo_1cyl = np.zeros(8)
    fo_1cyl[0] = mass_osc * stroke / 2 * om2
    fo_1cyl[1] = fo_1cyl[0] * (lam + 1 / 4 * lam ** 3 + 15 / 128 * lam ** 5)
    fo_1cyl[2] = 0
    fo_1cyl[3] = fo_1cyl[0] * (-1 / 4 * lam ** 3 - 3 / 16 * lam ** 5)
    fo_1cyl[4] = 0
    fo_1cyl[5] = fo_1cyl[0] * (9 / 128 * lam ** 5)
    fo_1cyl[6] = 0
    fo_1cyl[7] = fo_1cyl[0] * (-1 / 39 * lam ** 7)
    harm_ord = np.arange(1, 9)
    n_harm = len(harm_ord)

    # For each throw angle combination
    if throw_angles_mat.shape[0] != n_throw:
        raise ValueError("Number of define throw angles must match number of throws.")
    if throw_angles_mat.ndim == 1:
        throw_angles_mat = throw_angles_mat[:, None]
    n_cases = throw_angles_mat.shape[1]

    # Init
    n_phi = len(phi)
    ratio_r_mat = np.zeros(n_cases)
    fry_mat = np.zeros((n_phi, n_cases))
    frz_mat = np.zeros((n_phi, n_cases))
    mry_mat = np.zeros((n_phi, n_cases))
    mrz_mat = np.zeros((n_phi, n_cases))
    foy_mat = np.zeros((n_harm, n_phi, n_cases))
    foz_mat = np.zeros((n_harm, n_phi, n_cases))
    moy_mat = np.zeros((n_harm, n_phi, n_cases))
    moz_mat = np.zeros((n_harm, n_phi, n_cases))

    for indcase in range(n_cases):

        # Throw angles for this case
        angle_throws = throw_angles_mat[:, indcase]  # deg
        at_rad = angle_throws * np.pi / 180  # Convert to radians

        # Oscillating masses angles
        angle_osc = angle_bank - np.array([a for a in angle_throws for i in range(2)])
        ao_rad = angle_osc * np.pi / 180  # Convert to radians
        
        # Rotating forces
        # Counterweights
        fr_cw_1throw = -2 * mass_cw * r_cw * om2
        fr_cw = np.sum(fr_cw_1throw * np.exp(1j * at_rad))
        # Rest of masses
        fr_rest_1throw = 2 * mass_web * r_web * om2 + (mass_pin + 2 * mass_con_be) * stroke / 2 * om2
        fr_rest = np.sum(fr_rest_1throw * np.exp(1j * at_rad))
        # Total rotating force
        fr = fr_cw + fr_rest
        # Horizontal and vertical components
        fry, frz = rotating2cartesian(fr, phi, type='force')
        # Balancing ratio
        ratio_fr = np.abs(fr_cw / fr_rest)
        # ratio_fr = -np.real(fr_cw * np.conj(fr_rest)) / np.abs(fr_rest) ** 2

        # Rotating moments
        # Counterweights
        mr_cw = np.sum(fr_cw_1throw * x_throw * np.exp(1j * at_rad))
        # Rest of masses
        mr_rest = np.sum(fr_rest_1throw * x_throw * np.exp(1j * at_rad))
        # Total rotating
        mr = mr_cw + mr_rest
        # Horizontal and vertical components
        mry, mrz = rotating2cartesian(mr, phi, type='moment')
        # Balancing ratio
        ratio_mr = np.abs(mr_cw / mr_rest)
        
        # Rotating balancing ratio
        if np.abs(fr_cw) > 1e-6 and np.abs(fr_rest) > 1e-6:
            ratio_r = ratio_fr
        elif np.abs(mr_cw) > 1e-6 and np.abs(mr_rest) > 1e-6:
            ratio_r = ratio_mr
        else:
            ratio_r = np.nan

        # Oscillating forces and moments
        foy_complex = np.zeros(n_harm, dtype=complex)
        foz_complex = np.zeros(n_harm, dtype=complex)
        moy_complex = np.zeros(n_harm, dtype=complex)
        moz_complex = np.zeros(n_harm, dtype=complex)
        for indcyl in range(n_cyl):
            fo_1cyl_y, fo_1cyl_z = projection_yz(fo_1cyl, angle_bank[indcyl])
            foy_complex += fo_1cyl_y * np.exp(-1j * harm_ord * ao_rad[indcyl])
            foz_complex += fo_1cyl_z * np.exp(-1j * harm_ord * ao_rad[indcyl])
            moy_complex += -fo_1cyl_z * x_cyl[indcyl] * np.exp(-1j * harm_ord * ao_rad[indcyl])
            moz_complex += fo_1cyl_y * x_cyl[indcyl] * np.exp(-1j * harm_ord * ao_rad[indcyl])
        foy = complex2crankangle(foy_complex, harm_ord, phi)
        foz = complex2crankangle(foz_complex, harm_ord, phi)
        moy = complex2crankangle(moy_complex, harm_ord, phi)
        moz = complex2crankangle(moz_complex, harm_ord, phi)

        # Store results
        ratio_r_mat[indcase] = ratio_r
        fry_mat[:, indcase] = fry
        frz_mat[:, indcase] = frz
        mry_mat[:, indcase] = mry
        mrz_mat[:, indcase] = mrz
        foy_mat[:, :, indcase] = foy
        foz_mat[:, :, indcase] = foz
        moy_mat[:, :, indcase] = moy
        moz_mat[:, :, indcase] = moz
        
    # If only one case, remove the case dimension
    if n_cases == 1:
        ratio_r_mat = ratio_r_mat[0]
        fry_mat = fry_mat[:, 0]
        frz_mat = frz_mat[:, 0]
        mry_mat = mry_mat[:, 0]
        mrz_mat = mrz_mat[:, 0]
        foy_mat = foy_mat[:, :, 0]
        foz_mat = foz_mat[:, :, 0]
        moy_mat = moy_mat[:, :, 0]
        moz_mat = moz_mat[:, :, 0]

    return ratio_r_mat, fry_mat, frz_mat, mry_mat, mrz_mat, harm_ord, foy_mat, foz_mat, moy_mat, moz_mat