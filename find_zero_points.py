from math import log10

def m(f):
    """
    calculate the apparent/instrumental magnitude through a given filter.
    
    :param f: the flux through that particular filter.
    """
    return round(-2.5*log10(f),2)


def bv(flux_b, flux_v, zp_blue, zp_visual):
    """
    calculate and return a magnitude difference, i.e. the B-V index, for two images
    
    :param flux_b: flux through the bluer filter
    :param flux_v: flux through the visual filter
    """

    m_blue = -2.5 * log10(flux_b) + zp_blue
    m_visual = -2.5 * log10(flux_v) + zp_visual
    return round(m_blue - m_visual, 2)


# Published values of v and b-v for the moon, and the b value derived from it.
v = -12.75
b_v = 0.94
b = v + b_v
print('Published moon magnitude in visual filter: {}'.format(v))
print('Published B-V of moon: {}'.format(b_v))
print('Magnitude in blue filter (calculated): {}'.format(b))
print('(Published values from Gallouet 1963)')
print

# fluxes for each filter. Taken from photometries ==============================
# these values are from the 10 April moon data set, and the flux column.
fnone = 67494.06

# visual-er filters: filters with their dominant/central wavelength > 550 nm
f11 = 40216.71
f15 = 27083.56
fred = 12787.48
fgreen = 22084.62

# bluer filters: filters with their dominant/central wavelength < 550 nm
f47 = 1651.552
f82a = 59623.73
fblue = 13976.66
flum = 60027.88

# Calculating zero points ======================================================
# filter #11 -------------------------------------------------------------------
m_moon_11 = m(f11)
zp_b_11 = b - m_moon_11
zp_v_11 = v - m_moon_11

print('Apparent magnitude of moon (our camera, filter #11, 0.7 millisec)'
      ': {}'.format(m_moon_11))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter #11')
print('blue: {}, visual: {}'.format(zp_b_11, zp_v_11))
print

# filter #15 -------------------------------------------------------------------
m_moon_15 = m(f15)
zp_b_15 = b - m_moon_15
zp_v_15 = v - m_moon_15

print('Apparent magnitude of moon (our camera, filter #15, 0.7 millisec)'
      ': {}'.format(m_moon_15))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter #15')
print('blue: {}, visual: {}'.format(zp_b_15, zp_v_15))
print

# filter LRGB red --------------------------------------------------------------
m_moon_red = m(fred)
zp_b_red = b - m_moon_red
zp_v_red = v - m_moon_red

print('Apparent magnitude of moon (our camera, filter LRGB red, 0.7 millisec)'
      ': {}'.format(m_moon_red))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter LRGB red')
print('blue: {}, visual: {}'.format(zp_b_red, zp_v_red))
print

# filter LRGB green -----------------------------------------------------------
m_moon_green = m(fgreen)
zp_b_green = b - m_moon_green
zp_v_green = v - m_moon_green

print('Apparent magnitude of moon (our camera, filter LRGB green, 0.7 millisec)'
      ': {}'.format(m_moon_green))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter LRGB green')
print('blue: {}, visual: {}'.format(zp_b_green, zp_v_green))
print

# filter #47 -------------------------------------------------------------------
m_moon_47 = m(f47)
zp_b_47 = b - m_moon_47
zp_v_47 = v - m_moon_47

print('Apparent magnitude of moon (our camera, filter #47, 0.7 millisec)'
      ': {}'.format(m_moon_47))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter #47')
print('blue: {}, visual: {}'.format(zp_b_47, zp_v_47))
print

# filter #82a ------------------------------------------------------------------
m_moon_82a = m(f82a)
zp_b_82a = b - m_moon_82a
zp_v_82a = v - m_moon_82a

print('Apparent magnitude of moon (our camera, filter #82a, 0.7 millisec)'
      ': {}'.format(m_moon_82a))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter #82a')
print('blue: {}, visual: {}'.format(zp_b_82a, zp_v_82a))
print

# filter LRGB luminance --------------------------------------------------------
m_moon_lum = m(flum)
zp_b_lum = b - m_moon_lum
zp_v_lum = v - m_moon_lum

print('Apparent magnitude of moon (our camera, filter LRGB luminance, '
      '0.7 millisec)'
      ': {}'.format(m_moon_lum))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter #lum')
print('blue: {}, visual: {}'.format(zp_b_lum, zp_v_lum))    
print

# filter LRGB blue --------------------------------------------------------------
m_moon_blue = m(fblue)
zp_b_blue = b - m_moon_blue
zp_v_blue = v - m_moon_blue

print('Apparent magnitude of moon (our camera, filter LRGB blue, 0.7 millisec)'
      ': {}'.format(m_moon_blue))
print('Calculated zero point using published values and measured moon magnitude'
      ' in filter #blue')
print('blue: {}, visual: {}'.format(zp_b_blue, zp_v_blue))
print

# Calculate B-V values at long last ============================================

print('Moon B-V values in various filters')
print('==================================')
print('LRGBblue-11: {}'.format(bv(fblue, f11, zp_b_blue, zp_v_11)))
print('LRGBblue-15: {}'.format(bv(fblue, f15, zp_b_blue, zp_v_15)))
print('LRGBblue-LRGB red: {}'.format(bv(fblue, fred, zp_b_blue, zp_v_red)))
print('LRGB blue-LRGB green: {}'.format(bv(fblue, fgreen, zp_b_blue, zp_v_green)))
print
print('82a-11: {}'.format(bv(f82a, f11, zp_b_82a, zp_v_11)))
print('82a-15: {}'.format(bv(f82a, f15, zp_b_82a, zp_v_15)))
print('82a-LRGB red: {}'.format(bv(f82a, fred, zp_b_82a, zp_v_red)))
print('82a-LRGB green: {}'.format(bv(f82a, fgreen, zp_b_82a, zp_v_green)))
print
print('47-11: {}'.format(bv(f47, f11, zp_b_47, zp_v_11)))
print('47-15: {}'.format(bv(f47, f15, zp_b_47, zp_v_15)))
print('47-LRGB red: {}'.format(bv(f47, fred, zp_b_47, zp_v_red)))
print('47-LRGB green: {}'.format(bv(f47, fgreen, zp_b_47, zp_v_green)))
print
print('LRGB lum-11: {}'.format(bv(flum, f11, zp_b_lum, zp_v_11)))
print('LRGB lum-15: {}'.format(bv(flum, f15, zp_b_lum, zp_v_15)))
print('LRGB lum-LRGB red: {}'.format(bv(flum, fred, zp_b_lum, zp_v_red)))
print('LRGB lum-LRGB green: {}'.format(bv(flum, fgreen, zp_b_lum, zp_v_green)))
