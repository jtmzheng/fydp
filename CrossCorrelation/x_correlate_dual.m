% Input: Measured sample, Sampling Frequency, Reference sample

function [ sample_lag, time_lag] = x_correlate_dual(sample_test ,sample_reference ,sampling_freq)

time_reference = (0:length(sample_reference)-1)/sampling_freq;
time_sample = (0:length(sample_test)-1)/sampling_freq;

% acquire data from x-correlation - correlation data array and lag value
[acor,lag] = xcorr(sample_reference,sample_test,sampling_freq);

[~,I] = max(abs(acor));

% number of samples needed to line up signals
sample_lag = lag(I);

% time (in sec) delay between signals
time_lag = sample_lag/sampling_freq;

% % plot x-correlation data
% figure();
% plot(lag,acor)

% using the lag value to shift signal to line up with refernce
shifted_aligned_signal = sample_test((-sample_lag+1):end);

% time axis for shifted signal
time_axis_aligned_sig = (0:length(shifted_aligned_signal)-1)/sampling_freq;

% plot shifted signal and 
figure();
subplot(2,1,1)
plot(time_sample,sample_test,'-r');
hold on;
plot(time_axis_aligned_sig,shifted_aligned_signal,'b');
hold off;
legend('Unshifted','Shifted');
title('Aligned Sample')

subplot(2,1,2)
plot(time_reference,sample_reference,'r');
title('Reference Signal');
xlabel('Time (s)');

end

