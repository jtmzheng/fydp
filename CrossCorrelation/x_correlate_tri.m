% Input: Sample 1, Sample 2, Sample 3, Sampling Frequency and Reference sample  

function [output_array] = x_correlate_tri( sample_1_data , sample_2_data , ...
    sample_3_data , sampling_freq, sample_ref_data)

% setup time axis for plotting
sample_1_time = (0:length(sample_1_data)-1)/sampling_freq;
sample_2_time = (0:length(sample_2_data)-1)/sampling_freq;
sample_3_time = (0:length(sample_3_data)-1)/sampling_freq;
sample_ref_time = (0:length(sample_ref_data)-1)/sampling_freq;

% plot all 3 original signals, and one plot for reference signal
figure();
subplot(411);
plot(sample_1_time,sample_1_data,'b');
title('Original Signal A');

subplot(412);
plot(sample_2_time,sample_2_data,'g');
title('Original Signal B');

subplot(413);
plot(sample_3_time,sample_3_data,'k');
title('Original Signal C');

subplot(414);
plot(sample_ref_time,sample_ref_data,'r');
title('Reference Sequence');

% 3 combinations for correlation
[sample_lag_1_2, time_lag_1_2] = x_correlate_dual(sample_1_data,sample_ref_data,sampling_freq);
[sample_lag_1_3, time_lag_1_3] = x_correlate_dual(sample_2_data,sample_ref_data,sampling_freq);
[sample_lag_2_3, time_lag_2_3] = x_correlate_dual(sample_3_data,sample_ref_data,sampling_freq);

% Arrays containing data
AR = [sample_lag_1_2, time_lag_1_2];
BR = [sample_lag_1_3, time_lag_1_3];
CR = [sample_lag_2_3, time_lag_2_3];

% concatonating arrays to make single output
output_array = vertcat(AR,BR,CR);


end

