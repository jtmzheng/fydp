function [ sample_lag, time_lag] = x_correlate_dual( s1 ,ref_seq , Fs)

t1 = (0:length(s1)-1)/Fs;
ref_t = (0:length(ref_seq)-1)/Fs;

[acor,lag] = xcorr(ref_seq,s1, Fs);

[~,I] = max(abs(acor));
sample_lag = lag(I)
time_lag = sample_lag/Fs;

f1 = figure();
plot(lag,acor)
a3 = gca;

% a3.XTick = sort([-10000:1000:10000 sample_lag]);

    s1al = s1((-sample_lag+1):end);
    t1al = (0:length(s1al)-1)/Fs;


t1al = (0:length(s1al)-1)/Fs;

f2 = figure();
subplot(2,1,1)
plot(t1al,s1al,'b')
title('Aligned Sample')

subplot(2,1,2)
plot(ref_t,ref_seq,'r')
title('Reference Signal')
xlabel('Time (s)');

end

