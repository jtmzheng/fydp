%*************************************************************************
% Written by: Samarth Kochhar
% Mechatronics Engineering 
% University of Waterloo
% ID 20419203
%*************************************************************************

% initization
clc;
clear all;
format compact;
close all;
% ------------------------------------------------------------------------

% start clock
tic;

% import audio files from same directory as x-corr project
[sample_1_data,sampling_freq] = audioread('macRec.aiff');
[sample_2_data,sampling_freq] = audioread('iphoneRec.m4a');
sample_3_data = sample_1_data;
% sample 3 same as 1; force delay by 40000 samples to test program
for i = 1:length(sample_3_data)
    if i < length(sample_3_data)-40000
         sample_3_data(i,1) = sample_3_data(i+40000,1);
    else if i >= length(sample_3_data)-40000
            sample_3_data(i,1) = 0;
        end
    end
end

% audio file outputs as dual channel, take only one channel input
sample_1_data = sample_1_data(1:length(sample_1_data),1);

% audio file outputs as dual channel, take only one channel input
sample_2_data = sample_2_data(:,1);

% audio file outputs as dual channel, take only one channel input
% also scale amplitude by 0.5 to get some variation in audio signal
sample_3_data = 0.5*sample_3_data(1:length(sample_3_data),1);

% run a 3 signal x-correlation with lag_sample_time as output array
lag_sample_time = x_correlate_tri(sample_1_data, sample_2_data, ...
    sample_3_data, sampling_freq, sample_3_data);

% sample lag = Real #
lag_sample = abs(lag_sample_time(:,1));

% time lag = sec
lag_time = abs(lag_sample_time(:,2));

% stop clock
toc;