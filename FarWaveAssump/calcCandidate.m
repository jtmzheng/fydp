% Calculate candidate vectors
function [cand, candStar] = calcCandidate(d1, d2, p1, p2)
    vs = 340.29;
    d = abs(d1 - d2) * vs;
    l = (p2 - p1)/norm(p2 - p1); % unit vector between mics
    theta = acos(d/norm(p2 - p1));
    
    cand = calcSingleCand(theta, l);
    candStar = calcSingleCand(-theta, l);
end

function [cand] = calcSingleCand(beta, l)
    rotBeta = [cos(beta), -sin(beta); sin(beta), cos(beta)];
    cand = rotBeta * l;
end