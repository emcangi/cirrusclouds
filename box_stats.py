def real_m_stats(self, x, y, data=None):
    """report the statisics of values in a box with side region_size.
    The statistics are mean, std, median, min, max.
    Parameters
    ----------
    x: int
        The x location of the object
    y: int
        The y location of the object
    data: numpy array
        The data array to work on
    """
    import numpy as np 
    import logging 

    if data is None:
        data = self._data

    region_size = self.report_stat_pars["region_size"][0]

    dist = region_size / 2
    xmin = int(x - dist)
    xmax = int(x + dist)
    ymin = int(y - dist)
    ymax = int(y + dist)

    stat = getattr(np, 'mean')
    stat2 = getattr(np, 'std')
    stat3 = getattr(np, 'median')
    stat4 = getattr(np, 'min')
    stat5 = getattr(np, 'max')

    cols = "SLICE   NPIX   MEAN   STD   MEDIAN   MIN   MAX\n"
    box = "[{}:{},{}:{}]  ".format(xmin, xmax, ymin, ymax)
    area = "{}  ".format(region_size)
    sr1 = " {}  ".format(stat(data[ymin:ymax, xmin:xmax]))
    sr2 = "{}  ".format(stat2(data[ymin:ymax, xmin:xmax]))
    sr3 = "{}  ".format(stat3(data[ymin:ymax, xmin:xmax]))
    sr4 = "{}  ".format(stat4(data[ymin:ymax, xmin:xmax]))
    sr5 = "{}".format(stat5(data[ymin:ymax, xmin:xmax]))
    pstr = cols + box + area + sr1 + sr2 + sr3 + sr4 + sr5

    print(pstr)
    logging.info(pstr)