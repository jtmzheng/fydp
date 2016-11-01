close all;
clear;
global l;
l = 0.3;                % distance between microphone to centroid
r = 19;                 % distance from origin
theta = 25 * (pi/180);   % angle CW from O-1 (radians)

x = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3+theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta));
y = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3-theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta));