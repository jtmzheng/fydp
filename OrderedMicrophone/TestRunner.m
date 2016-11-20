%% Calculation
clear; clc;

% Test data
r = linspace(0.3, 10, 10);
theta = degtorad(linspace(0, 240, 36));

% Generate every test combination of r, theta
[R, Theta] = meshgrid(r, theta);

% Constants
l = 0.3;                % distance between microphones
ss = 300;               % speed of sound (m/s)
err = 0.001;

[F1, F2] = calcRelativeDelay(R, Theta, l);
res = zeros(size(R));

for i=1:size(R,1)
    for k=1:size(R,2)
        theta = calcTheta(F1(i, k) + err, F2(i, k) + err, l);
        res(i, k) = theta;  % only keep angle
    end
end

%% Plotting
hold on;
surf(R, radtodeg(Theta), abs(res - rad2deg(Theta)));
grid on;
title('\fontsize{16}Error in angle reconstruction with 1 [ms] timing error');
xlabel('\fontsize{12}Distance [m]');
ylabel('\fontsize{12}Angle [deg]');
zlabel('\fontsize{12}Error [deg]');