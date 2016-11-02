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
        init_val = [5, pi/6];
        f = @(x)delayFunc(x, F1(i, k) + err, F2(i, k) + err, l);
        result = fsolve(f, init_val);
        res(i, k) = result(2);  % only keep angle
    end
end

%% Plotting
hold on;
mesh(R, radtodeg(Theta), radtodeg(res - Theta));