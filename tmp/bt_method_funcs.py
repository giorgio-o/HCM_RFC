    def get_bin_total_amount(self, EV, bin_, act):
        EV = Intervals(self.load('%s_timeSet' %act))
        coeff = 1000. * self.get_ingestion_coefficients(act)   # mg
        amount = EV.intersect(bin_).measure() * coeff
        return amount

    def get_bin_bout_intensities(self, B, bin_, act):
        EV = Intervals(self.load('%s_timeSet' %act))
        coeff = 1000. * self.get_ingestion_coefficients(act)   # mg
        BSet_this_bin = B.intersect(bin_)
        intensity = []
        # compute each bout intensity
        if not BSet_this_bin.is_empty():
            for this_bout in BSet_this_bin:
                i = EV.intersect(Intervals(this_bout)).measure() / Intervals(this_bout).measure() * coeff
                intensity.append(i)
        return np.array(intensity)




    def get_bin_bout_move_idx(self, first_B_start, last_B_end):
        T, idx_nhb, MB_idx = [self.load(var) for var in ['CT', 'idx_out_HB', 'MB_idx']]

        idx_bin = np.zeros(T.shape[0], dtype=bool)
        idx_start = np.searchsorted(T, first_B_start)
        idx_end = np.searchsorted(T, last_B_end, side='right')
        idx_bin[idx_start : idx_end] = True
        
        idx = MB_idx & idx_bin        
        return idx

    def get_bin_bout_distances(self, idx):
        dist, _ = self.get_move_events()
        return dist[idx]

    def get_bin_speed(self, idx, b_chunks):
        speed = []
        for start, end in b_chunks:
            s = dist[start:end].sum() / (T[end] - T[start])
            speed.append(s)
        return np.array(speed)