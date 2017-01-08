syms r theta;
global l x1 y1;

l = 0.3;

std_noise = 3e-3;
freq = 1e6;
speed_of_sound = 300;
error_samples = (std_noise / speed_of_sound) * freq;

x1 = x + std_noise.*randn();
y1 = y + std_noise.*randn();

f = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3+theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta)) - x1;
g = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3-theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta)) - y1;

figure; hold on; grid on;
h1 = ezplot(f, [0, 20, 0, pi/3]);
h2 = ezplot(g, [0, 20, 0, pi/3]);
set(h2, 'Color', 'r');

fun = @delayFunc;
init_val = [5, pi/6];
f = @(x)delayFunc(x, x1, y1, l);
result = fsolve(f, init_val);
ret_deg = result;

scatter(result(1), result(2), 'X');
