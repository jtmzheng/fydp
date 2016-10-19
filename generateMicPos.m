function [p1, p2, p3] = generateMicPos(r)
    p1 = [r/2; 0];
    p2 = [-(r/2)*cos(pi/6); -(r/2)*sin(pi/6)];
    p3 = [(r/2)*cos(pi/6); -(r/2)*sin(pi/6)];
end