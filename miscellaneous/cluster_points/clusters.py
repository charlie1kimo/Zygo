"""
clusters.py
"""

import numpy
import scipy.spatial

def clusterNeighbors(data, distance):
    """
        retval, avg ,sep, xydisp = clusterNeighbors(data, distance)
    @Purpose:
        Given a list of coordinates, clusters all points in data into a cluster set when those points
        are within given distance. Also the mean x,y coordinates of each
        cluster
    @Inputs:
        (numpy.array) data = given list of coordinates
        (int) distance = given radius distance
    @Outputs:
        (list) [[cluster1], [cluster2], [cluster3]]
        (numpy.array) [[meanx_cluster1,meany_cluster1],...]
        (list) [[cluster1_sep_mean],[cluster2_sep_mean], ...]
        (list) [[[cluster1_pt1_x_sep, cluster1_pt1_y_sep], [cluster1_pt2_x_sep, cluster1_pt2_y_sep]], ...]
        (list) [[cluster_pt1_xy_disp, cluster1_pt2_xy_disp], [cluster2_pt1_xy_disp, ...], ...]
    """
    import scipy.spatial
    retval = []
    processed_index = numpy.zeros(len(data))
    kdTree = scipy.spatial.KDTree(data)
    neighbors = kdTree.query_ball_tree(kdTree, distance)

    for pt_index in range(len(neighbors)):
        if processed_index[pt_index]:
            continue
        pt = data[pt_index]
        cluster = [pt]
        processed_index[pt_index] = 1
        for neighbor_index in neighbors[pt_index]:
            if processed_index[neighbor_index]:
                continue
        
            cluster.append(data[neighbor_index])
            processed_index[neighbor_index] = 1
        retval.append(numpy.array(cluster))

    avg = numpy.zeros((len(retval),2))
    for i in xrange(len(retval)):
        avg[i] = retval[i].mean(0)

    sep = []
    xydisp = []
    for clusterInd in xrange(len(retval)):
        sepClusterToAdd = []
        xyDispClusterToAdd = []
        for ptInd in xrange(len(retval[clusterInd])):
            x_sep = retval[clusterInd][ptInd][0] - avg[clusterInd][0]
            y_sep = retval[clusterInd][ptInd][1] - avg[clusterInd][1]
            pt = numpy.array([x_sep, y_sep])
            sepClusterToAdd.append(pt)

            xy_disp = numpy.sqrt(x_sep**2+y_sep**2)
            xyDispClusterToAdd.append(xy_disp)

        sep.append(numpy.array(sepClusterToAdd))
        xydisp.append(numpy.array(xyDispClusterToAdd))
            
    return retval, avg, sep, xydisp

