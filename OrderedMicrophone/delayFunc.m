function [F] = delayFunc(x, x1, y1, l)
    r = x(1);
    theta = x(2);
    F(1) = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3+theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta)) - x1;
    F(2) = sqrt(r^2 + l^2 - 2*l*r*cos(2*pi/3-theta)) - sqrt(r^2 + l^2 - 2*l*r*cos(theta)) - y1;
end