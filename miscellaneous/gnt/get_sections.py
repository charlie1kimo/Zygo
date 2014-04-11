"""
This module used to develop a get_sections method to be added to the
ompy.gnt.Gnt class

"""

def get_sections(gobj, sizeThreshold=30):
    """
    gs = get_sections(gobj, sizeThreshold=30)
    
    Finds sections of connected components areas of the Gnt and breaks
    them into unconnected sections and returns them as separate Gnts in
    a GntSet. 

    Uses scipy.ndimage.measurements.label functions to divide the sections
    http://docs.scipy.org/doc/scipy-0.11.0/reference/generated/scipy.ndimage.measurements.label.html#scipy.ndimage.measurements.label

    Input:
    gobj<Gnt> ompy.Gnt object
    sizeThreshold<int>(pixels)   size threshold to eliminate small faulty labels.

    Output:
    gs<GntSet> Contains separated area sections from input Gnt
    """
    import ompy.gntset as gntset
    import scipy.ndimage.measurements
    import numpy
    import time
    list_of_gnts = []
    #make list of Gnts using the scipy.ndimage.measurements.label function
    time_start = time.time()
    b_img = numpy.invert(gobj.z.mask).astype(int)
    (labeled_img, num_labels) = scipy.ndimage.measurements.label(b_img)
    for l in range(num_labels):
        new_gnt = gobj.copy()
        new_mask = labeled_img != l+1                       # set mask True if not current label value. (Avoided loop)
        new_gnt.z.mask = new_mask
        b_img_mask = numpy.invert(new_mask).astype(int)
        if numpy.sum(b_img_mask) > sizeThreshold:
            list_of_gnts.append(new_gnt)

    time_end = time.time()
    print "Processed time: %f seconds." % (time_end - time_start)
    return gntset.GntSet(list_of_gnts)
    
