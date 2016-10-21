close all;
clear;
global l;
l = 0.3;
r = 19;
theta = 25* (pi/180);

x = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3+theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta));
y = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3-theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta));