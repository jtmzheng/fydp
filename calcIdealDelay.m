function [d1, d2, d3] = calcIdealDelay(s, p1, p2, p3)
    % Speed of sound in m/s
    c = 340.29;
    d1 = norm(s - p1)/c;
    d2 = norm(s - p2)/c;
    d3 = norm(s - p3)/c;
end