function [op] = x_correlate_tri( seq_a , seq_b , seq_c , Fs, ref_seq)

t_a = (0:length(seq_a)-1)/Fs;
t_b = (0:length(seq_b)-1)/Fs;
t_c = (0:length(seq_c)-1)/Fs;
t_ref = (0:length(ref_seq)-1)/Fs;

figure();
subplot(311);
plot(t_a,seq_a);
title('Original Signal A');

subplot(412);
plot(t_b,seq_b);
title('Original Signal B');

subplot(413);
plot(t_c,seq_c);
title('Original Signal C');

subplot(414);
plot(t_c,ref_seq,'r');
title('Reference Sequence');

[a_b_corr, a_b_lag] = x_correlate_dual(seq_a,ref_seq,Fs);
[a_c_corr, a_c_lag] = x_correlate_dual(seq_b,ref_seq,Fs);
[b_c_corr, b_c_lag] = x_correlate_dual(seq_c,ref_seq,Fs);

AR = [a_b_corr, a_b_lag];
BR = [a_c_corr, a_c_lag];
CR = [b_c_corr, b_c_lag];

op = vertcat(AR,BR,CR);


end

