%% Calculation
clear; clc;

% Test data
r = 2;
theta = deg2rad(30);
L = 3;

% Map to Cartesian
s = [r .* sin(theta), r .* cos(theta)];

% First mic at (0, 0), second mic array at (L, 0)
sPrime = [s(1) - L, s(2)];

rPrime = norm(sPrime);
thPrime = atan2(sPrime(1), sPrime(2));

% Constants
l = 0.3;                % distance between microphones
ss = 300;               % speed of sound (m/s)
err = linspace(-0.001, 0.001, 10);  % up to 1 ms error
res = zeros(length(err).*length(err), 2);

figure; hold on;
scatter(s(1), s(2));
grid on;

cnt = 1;
for i=1:length(err)
    for j=1:length(err)
    [f1, f2] = calcRelativeDelay(r, theta, l);
    [f3, f4] = calcRelativeDelay(rPrime, thPrime, l);

    th1 = calcTheta(f1 + err(i), f2 + err(i), l);
    th2 = calcTheta(f3 + err(j), f4 + err(j), l);

    % NB: Fix calcPOI to work with col or row vectors
    v1 = [sin(deg2rad(th1)), cos(deg2rad(th1))]';
    v2 = [sin(deg2rad(th2)), cos(deg2rad(th2))]';
    p1 = [0, 0]';
    p2 = [L, 0]';

    res(cnt, :) = calcPOI(p1, p2, v1, v2);
    cnt = cnt + 1;
    end
end

scatter(res(:, 1), res(:, 2));
scatter(0, 0, 'filled');
scatter(L, 0, 'filled');