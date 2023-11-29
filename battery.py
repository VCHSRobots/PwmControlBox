# Reads Battery Voltage
# dlb, Nov 2023

# After some experimenting with reading ADC(3) which is fed from a
# voltage divider, from the battery, and then doing a least squares
# linear fit, we found that V = 0.00061*r - 0.12333.

# After more experimenting, we found this is accurate to about 0.1 volts
# over a range of 1.8 to 5.4 volts.


import machine

voltpin = machine.ADC(3)

def get_voltage():
    ''' Returns the voltage at the battery.'''
    r = voltpin.read_u16()
    v = 0.00061 * r - 0.12333
    return v


