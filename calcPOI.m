function [s] = calcPOI(p1, p2, v1, v2)
    % solve parametric system of equations for POI
    par = [v1(1), -v2(1); v1(2), -v2(2)]^-1 * (p2 - p1); %[t, s]
    s = p1 + par(1) * v1; % or p2 + par(2)*v2;
end