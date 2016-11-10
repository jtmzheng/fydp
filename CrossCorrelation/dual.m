% To create a simple sinusoidal signal:
clc;
clear all;
format compact;
close all;
% ------------------------------------------------------------------------

tic;

[y2,Fs] = audioread('iphoneRec.m4a');
[y1,Fs] = audioread('macRec.aiff');
[y3,Fs] = audioread('macRec.aiff');

for i = 1:length(y3)
    if i < length(y3)-40000
         y3(i,1) = y3(i+40000,1);
    else if i >= length(y3)-40000
            y3(i,1) = 0;
        end
    end
end

y2 = y2(:,1);

x1 = linspace(0,length(y1)/Fs,length(y1));
x1 = x1';
x2 = linspace(0,length(y2)/Fs,length(y2));
x2 = x2';
x3 = linspace(0,length(y3)/Fs,length(y3));
x3 = x3';

y1 = y1(1:length(y2),1);
x1 = x1(1:length(x2),1);
y3 = 0.5*y3(1:length(y2),1);
x3 = x3(1:length(x2),1);

% figure();
% subplot(211)
% plot(x1,y1)
% subplot(212)
% plot(x2,y2)


s1 = y1;
t1 = x1;
s2 = y2;
t2 = x2;
s3 = y3;
t3 = x3;

AB = x_correlate_tri(s1, s2, s3, Fs, s3);

lag_times = abs(AB(:,2)) 

% [lag, time, f1, f2] = x_correlate_dual(s1,s2, Fs);

toc;