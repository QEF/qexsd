#
# Copyright (c), 2015-2016, Quantum Espresso Foundation and SISSA (Scuola
# Internazionale Superiore di Studi Avanzati). All rights reserved.
# This file is distributed under the terms of the MIT License. See the
# file 'LICENSE' in the root directory of the present distribution, or
# http://opensource.org/licenses/MIT.
# Authors: Davide Brunato, Giovanni Borghi
#
"""
Conversion functions for Quantum Espresso cards.
"""

import logging

# from .utils import set_logger

logger = logging.getLogger('qespresso')


#
# Functions for QE cards
#
def get_atomic_species_card(name, **kwargs):
    """
    Convert XML data to ATOMIC_SPECIES card

    :param name: Card name
    :param kwargs: Dictionary with converted data from XML file
    :return: List of strings
    """
    try:
        atomic_species = kwargs['atomic_species']
        species = atomic_species['species']
    except KeyError as err:
        logger.error("Missing required arguments when building ATOMIC_SPECIES card! %s" % err)
        return []

    lines = [name]
    try:
        lines.append(' {0} {1} {2}'.format(species['name'], species['mass'], species['pseudo_file']))
    except TypeError:
        for specie in species:
            lines.append(' {0} {1} {2}'.format(specie['name'], specie['mass'], specie['pseudo_file']))
    return lines


def get_atomic_positions_cell_card(name, **kwargs):
    """
    Convert XML data to ATOMIC_POSITIONS card

    :param name: Card name
    :param kwargs: Dictionary with converted data from XML file
    :return: List of strings
    """
    try:
        atomic_structure = kwargs['atomic_structure']
    except KeyError:
        logger.error("Missing required arguments when building ATOMIC_POSITIONS card!")
        return []
    # Find atoms
    atomic_positions =  atomic_structure.get('atomic_positions', {})
    wyckoff_positions = atomic_structure.get('wyckoff_positions', {})
    crystal_positions = atomic_structure.get('crystal_positions', {})
    units = 'bohr'
    try:
        is_wyckoff = False
        is_crystal = False
        if atomic_positions:
            atoms = atomic_positions['atom']
        elif wyckoff_positions:
            atoms = wyckoff_positions['atom']
            is_wyckoff = True
            units = 'crystal_sg'
        elif crystal_positions:
            atoms = crystal_positions['atom']
            is_crystal = True
            units = 'crystal'
        else:
            atoms = []
    except KeyError:
        logger.error("Cannot find any atoms for building ATOMIC_POSITIONS!")
        return []
    else:
        if not isinstance(atoms, list):
            atoms = [atoms]

    # Check atoms with position constraints
    free_positions = kwargs.get('free_positions', [])

    if free_positions:
        # Cover the case when free positions are provided for only one atom
        if type(free_positions[0]) not in (list, tuple):
            free_positions = [free_positions]

        if len(free_positions) != len(atoms):
            logger.error("ATOMIC_POSITIONS: incorrect number of position constraints!")

    # Add atomic positions
    lines = ['%s %s' % (name, units)]
    for k in range(len(atoms)):
        line = '{:4}'.format( atoms[k]['name'] )
        line += ' {:12.8f}  {:12.8f}  {:12.8f}'.format(*atoms[k]['_text'])
        #coords = ' '.join([str(value) for value in atoms[k]['_text']])

        if free_positions:
            #free_pos = ' '.join([str(value) for value in free_positions[k]])
            line += ' {:4d}{:4d}{:4d}'.format(*map(int, free_positions[k]))

        lines.append(line)

    return lines


def get_atomic_constraints_card(name, **kwargs):
    """
    Convert XML data to CONSTRAINTS card

    :param name: Card name
    :param kwargs: Dictionary with converted data from XML file
    :return: List of strings
    """
    try:
        atomic_constraints = kwargs['atomic_constraints']
    except KeyError:
        return []

    num_of_constraints = atomic_constraints['num_of_constraints']
    tolerance = atomic_constraints.get('tolerance')
    list_of_constraints = atomic_constraints['atomic_constraint']
    if len(list_of_constraints) != num_of_constraints:
        logger.error("The number of provided constraints is different from num_of_constraints")
    lines = [name]
    if tolerance:
        lines.append('{}  {}'.format(num_of_constraints, tolerance))
    else:
        lines.append('{}'.format(num_of_constraints))
    for constr in list_of_constraints:
        c_type  = constr['constr_type']
        parms = constr['constr_parms']
        if c_type in ['distance', 'planar_angle', 'torsional_angle']:
            parms = [int(_) for _ in parms]
        elif c_type in ['type_coord', 'atom_coord']:
            parms = [int(_) for _ in parms[:2]] + parms[2:]
        elif c_type in ['bennet_proj']:
            parms = [int(parms[0])]+parms[1:]
        target = constr['constr_target']
        constr_line = "'{}' "+ len(parms)*' {} ' + ' {}'
        lines.append(constr_line.format(*((c_type,)+tuple(parms)+(target,) )))
    return lines


def get_k_points_card(name, **kwargs):
    """
    Convert XML data to K_POINTS card

    :param name: Card name
    :param kwargs: Dictionary with converted data from XML file
    :return: List of strings
    """
    k_point = nk = monkhorst_pack= None
    gamma_only = kwargs.get('gamma_only', False)
    try:
        if not gamma_only:
            k_points_ibz = kwargs['k_points_IBZ']
            monkhorst_pack = k_points_ibz.get('monkhorst_pack', {})
            if monkhorst_pack:
                k_attrib = 'automatic'
            else:
                k_attrib = None
                k_point = k_points_ibz['k_point']
                nk = k_points_ibz['nk']
        else:
            k_attrib = 'gamma'

    except KeyError as err:
        logger.error("Missing required arguments when building K_POINTS card! %s" % err)
        return []
    else:
        if not isinstance(k_point, list):
            k_point = [k_point]

    lines = [name] if k_attrib is None else ['%s %s' % (name, k_attrib)]
    if k_attrib is None:
        lines.append(' %d' % nk)
        for point in k_point:
            lines.append(' {0} {1}'.format(
                ' '.join([str(value) for value in point['_text']]),
                point['weight'])
            )
    elif k_attrib == 'automatic':
        lines.append(' %(nk1)s %(nk2)s %(nk3)s %(k1)s %(k2)s %(k3)s' % monkhorst_pack)

    return lines


def get_atomic_forces_card(name, **kwargs):
    """
    Convert XML data to ATOMIC_FORCES card

    :param name: Card name
    :param kwargs: Dictionary with converted data from XML file
    :return: List of strings
    """
    try:
        external_atomic_forces = kwargs['external_atomic_forces']
    except KeyError:
        logger.debug("Missing required arguments when building ATOMIC_FORCES card!")
        return []
    if len(external_atomic_forces ) == 0:
       return []
    # Warning if number of atoms in atomic positions differ with forces
    try:
        atomic_positions = kwargs.get('atomic_positions', {})
    except KeyError:
        atomic_positions = kwargs.get('crystal_positions',{})
    atoms = atomic_positions.get('atom', [])
    if atoms and len(atoms) != len(external_atomic_forces):
        logger.error("incorrect number of atomic forces")

    # Build input card text lines
    lines = [name]
    for forces in external_atomic_forces:
        lines.append(' {0}'.format(' '.join([str(value) for value in forces])))
    return lines


def get_cell_parameters_card(name, **kwargs):
    """
    Convert XML data to CELL_PARAMETERS card

    :param name: Card name
    :param kwargs: Dictionary with converted data from XML file
    :return: List of strings
    """
    try:
        atomic_structure = kwargs['atomic_structure']
    except KeyError:
        logger.error("Missing required arguments when building ATOMIC_POSITIONS card!")
        return []
    # Add cell parameters card
    cells = atomic_structure.get('cell', {})
    if cells:
        lines = ['%s bohr' % name]
        for key in sorted(cells):
            if key not in ['a1', 'a2', 'a3']:
                continue
            lines.append( (3*'{:12.8f} ').format(*cells[key]))
        return lines
    return []


#
# Phonon Card
#
def get_qpoints_card(name, **kwargs):
    """
    :param name:
    :param kwargs:
    :return:
    """
    try:
        ldisp = kwargs['ldisp']
    except KeyError:
        ldisp = False
    if ldisp:
        return []

    try:
        qplot = kwargs['qplot']
    except KeyError:
        qplot = False
    try:
        ldisp = kwargs['ldisp']
    except KeyError:
        ldisp = False
    if not (qplot or ldisp):
        try:
            xq = kwargs['xq_dir']
        except KeyError:
            xq =[0.e0, 0.e0, 0.e0]
        line = "{:6.4f}  {:8.4f}  {:8.4f}".format(xq[0], xq[1], xq[2])
        return [line]
    lines=[]
    if (qplot):
        try:
            nqs = kwargs['nqs']
        except KeyError:
            nqs = 1
            raise RuntimeWarning("qplot was set to true in input but no value for nqs was provided assuming nqs = 1")
        lines.append('{:4d}'.format(nqs))
        q_points_list = kwargs['q_points_list']['q_point']
        for q_point in q_points_list:
            vector = ' '.join([str(coord) for coord in q_point['_text']])
            lines.append(' %s %s' % (vector, q_point['weight']))
    return lines

def get_climbing_images(name, **kwargs):
    manual_images = False
    try:
        if kwargs['climbingImage'] == 'manual' or kwargs['climbingImage'] == 'MANUAL':
            manual_images = True
    except KeyError:
        manual_images = False
    if manual_images:
        if isinstance(kwargs['climbingImageIndex'],list):
            line = [int(l) for l in kwargs['climbingImageIndex'] ]
            fmt  = len(line)*' %d, '
            line = fmt%tuple(line)
        else:
            line = ' %d ' % int(kwargs['climbingImageIndex'])
        return [line]
    return ['']

def get_neb_images_positions_card(name, **kwargs):
    """
    Extract atomic posisitions for each image provided in engine with an atomic_structure element
    :param name: Card name
    :param kwargs: List of dictionaries each containing an atomic_structure element.
    :return: List of lines
    """
    images = kwargs.get('atomic_structure',[])
    try:
        assert isinstance(images, list)
    except AssertionError:
        images=[images]
    if len(images) < 2:
        logger.error("At least the atomic structures for first and last image should be provided")
        return []
    first_positions = images[0].get('crystal_positions')
    units = 'crystal'
    if first_positions is None:
        first_positions = images[0].get('atomic_positions',{})
        units = 'bohr'
    his_nat = int(images[0].get('nat',0) )
    if units == 'crystal':
        last_positions = images[-1].get('crystal_positions',{})
    else:
        last_positions = images[-1].get('atomic_positions',{})
    if len(kwargs['atomic_structure']) > 2:
        if units == 'crystal':
            interm_pos = [ats.get('crystal_positions',{}) for ats in images[1:-1] ]
        else:
            interm_pos = [ats.get('atomic_positions',{})  for ats in images[1:-1]]
    else:
        interm_pos = []

    lines = ['%s '%'BEGIN_POSITIONS']
    lines.append('%s '%'FIRST_IMAGE')
    atoms = first_positions.get('atom',[])
    my_nat = len (atoms)
    if my_nat <= 0:
        logger.error("No atomic coordinates provided for first image")
        return ''
    if my_nat != his_nat:
        logger.error ( "nat provided in first image differs from number of atoms in atomic_positions!!!")

    free_positions = kwargs.get('free_positions', [])
    if free_positions and len(free_positions) != len(atoms):
        logger.error("ATOMIC_POSITIONS: incorrect number of position constraints!")

    lines.append ('%s { %s }' % ('ATOMIC_POSITIONS', units) )
    for k in range(len(atoms)):
        sp_name = '{:4}'.format(atoms[k]['name'])
        coords = '{:12.8f}  {:12.8f}  {:12.8f}'.format(*atoms[k]['_text'])
        if k < len(free_positions):
            free_pos = '{:4d}{:4d}{:4d}'.format(*[int(value) for value in free_positions[k]])
            lines.append('%s %s %s' % (sp_name, coords, free_pos))
        else:
            lines.append('%s %s' % (sp_name, coords))

    for inter in interm_pos:
        atoms = inter['atom']
        if len(atoms) != my_nat:
            logger.error('Found images with differing number of atoms !!!')

        lines.append('%s '%'INTERMEDIATE_IMAGE')
        lines.append('%s { %s }'% ('ATOMIC_POSITIONS', units) )
        for k in range(len(atoms)):
            sp_name = '{:4}'.format(atoms[k]['name'])
            coords = '{:12.8f}  {:12.8f}  {:12.8f}'.format(*atoms[k]['_text'])
            if k < len(free_positions):
                free_pos = '{:4d}{:4d}{:4d}'.format(*[int(value) for value in free_positions[k]])
                lines.append('%s %s %s' % (sp_name, coords, free_pos))
            else:
                lines.append('%s %s' % (sp_name, coords))
    atoms=last_positions['atom']
    if len(atoms) != my_nat:
        logger.error('Found images with differing number of atoms !!!')
    lines.append('%s '%'LAST_IMAGE')
    lines.append('%s { %s }'%('ATOMIC_POSITIONS', units) )
    for k in range(len(atoms)):
        sp_name = '{:4}'.format(atoms[k]['name'])
        coords = '{:12.8f}  {:12.8f}  {:12.8f}'.format(*atoms[k]['_text'])
        if k < len(free_positions):
            free_pos = '{:4d}{:4d}{:4d}'.format(*[int(value) for value in free_positions[k]])
            lines.append('%s %s %s' % (sp_name, coords, free_pos))
        else:
            lines.append('%s %s' % (sp_name, coords))
    lines.append( '%s '%'END_POSITIONS')
    return lines

def get_neb_cell_parameters_card (name, **kwargs):
    """
    Extract cell parameter from the firt of the atomic_structure elements provided in engine
    :param name: Card name
    :param kwargs: list of the atomic_structure dictionaries translate for xml element engine
    :return: list of text lines for the cell parameters card
    """
    images = kwargs.get('atomic_structure',[])
    try:
        assert isinstance(images,list)
    except AssertionError:
        images = [images]

    if len(images) < 1:
        logger.error (" No atomic_strucure element found in kwargs !!!")
        return ''

    atomic_structure  = images[0]
    cells = atomic_structure.get('cell', {})
    if cells:
        lines = ['%s bohr' % name]
        for key in sorted(cells):
            if key not in ['a1', 'a2', 'a3']:
                continue
            lines.append( (3*'{:12.8f}').format(*cells[key]) )
        return lines
    return []


def get_neb_atomic_forces_card   (name, **kwargs):
    pass
