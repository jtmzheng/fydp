% Assuming equilateral triangle configuration for mic
% l centroidal distance to each mic
% Calculates relative delay to each microphone
% NB: Accepts matrices for r, theta where they MUST be the same dim
% NB: Theta is the angle from the axis for the closest microphone to
% centroid-source line
function [f1, f2] = calcRelativeDelay(r, theta, l)
    f1 = sqrt(r.^2 + l.^2 - 2.*l.*r.*cos(2*pi/3 + theta)) - sqrt(r.^2 + l.^2 - 2.*l.*r.*cos(theta));
    f2 = sqrt(r.^2 + l.^2 - 2.*l.*r.*cos(2*pi/3 - theta)) - sqrt(r.^2 + l.^2 - 2.*l.*r.*cos(theta));
end