AS = np.array([[  60760.89,   61598.35],
       [  67075.57,   68231.25],
       [  70228.17,   77955.97],
       [  80299.79,   87991.97],
       [  91929.79,   92653.19],
       [  96743.81,   98864.99],
       [ 102078.49,  102319.65],
       [ 103589.11,  105060.67],
       [ 106308.59,  112852.87],
       [ 123752.27,  125047.47]])

bins = [np.array([[ 54000.,  61200.]]), np.array([[ 61200.,  68400.]]), np.array([[ 68400.,  75600.]]), np.array([[ 75600.,  82800.]]), np.array([[ 82800.,  90000.]]), np.array([[ 90000.,  97200.]]), np.array([[  97200.,  104400.]]), np.array([[ 104400.,  111600.]]), np.array([[ 111600.,  118800.]]), np.array([[ 118800.,  126000.]]), np.array([[ 126000.,  133200.]])]



from ceppa.util.intervals import Intervals

def count_onsets_in_bin(I, bin_):
    bin_start, bin_end = bin_
    I_bin_ = Intervals(I).intersect(Intervals(bin_))
    if I_bin_.is_empty():
        return 0, 0, np.array([[]])
    else:
        bin_time = 0
        cnt = 0     # onsets
        for start, end in I:
            if (start > bin_start and start < bin_end):
                bin_time += end - start
                if cnt < 1:
                    first_I_start = start
                last_I_end = end
                cnt +=1
        if cnt == 0:
            first_I_start, last_I_end = I_bin_.intervals[0]
    return cnt, bin_time, np.array([[first_I_start, last_I_end]])



arr = np.zeros(len(bins))
cnt, b = 0, 0
print "bin_CT\t\tcnt\tbin_time\tbin_eff\t\t\t\tASD"
for bin_ in bins:

    cnt, bin_time, bin_eff = count_onsets_in_bin(AS, bin_[0])
    print bin_[0]/3600.-7, '\t', cnt, '\t', bin_time/60., '\t', bin_eff/3600.-7, '\t', bin_time / cnt / 60. if cnt >0 else 0.
    if cnt > 0:
        arr[b] = bin_time / cnt / 60.    # minutes
    b +=1

arr = np.zeros(len(bins))
b = 0
for bin_ in bins:
    AS_time = Intervals(AS).intersect(Intervals(bin_)).measure()  #sec
    print AS_time/60.
    b +=1


