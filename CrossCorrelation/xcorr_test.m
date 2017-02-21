X = csvread('./messRound3b.csv');
VarName1 = medfilt1(X(:,1), 20);
VarName2 = medfilt1(X(:,3), 20);
VarName1 = VarName1 - mean(VarName1);
VarName2 = VarName2 - mean(VarName2);

fc1 = 500;
fc2 = 5000;
fs = 9.6e6;
[b,a] = butter(1,[fc1 fc2]/(fs/2), 'bandpass');
freqz(b,a)
VarName1 = filter(b,a,VarName1);
VarName2 = filter(b,a,VarName2);

VarName1 = VarName1 - min(VarName1(:));
VarName1 = VarName1 ./ max(VarName1(:));
VarName2 = VarName2 - min(VarName2(:)); 
VarName2 = VarName2 ./ max(VarName2(:));

prefix_idx1 = find(VarName1 < 0.05 | VarName1 > 0.95, 1);
prefix_idx2 = find(VarName2 < 0.05 | VarName2 > 0.95, 1);
start_idx = max(1, min((prefix_idx1 - 20e3), (prefix_idx2 - 20e3)));
sig1 = VarName1;
sig2 = VarName2;
sig1_offset = median(sig1);
sig2_offset = median(sig2);

sig1 = sig1(start_idx:prefix_idx1) - sig1_offset;
sig2 = sig2(start_idx:prefix_idx2) - sig2_offset;

[acor, lag] = xcorr(sig1, sig2);
[~, I] = max(acor);
sample_lag = lag(I)

if (sample_lag >= 0)
    plot(sig1(sample_lag+1: end)); hold on; plot(sig2);
else
    plot(sig1); hold on; plot(sig2(-sample_lag: end))
end

figure(2);
plot(VarName1); hold on; plot(VarName2);