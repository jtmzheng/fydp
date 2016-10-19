% Calculate candidate vectors by solving cosine law
function [cand, candStar] = calcCandidate(d1, d2, p1, p2)
    vs = 340.29;
    a = d2 * vs;
    b = d1 * vs;
    c = norm(p1 - p2);
    
    gamma = acos((a*a + b*b - c*c)/(2*a*b));
    alpha = asin(a*sin(gamma)/c);
    beta = pi/2 - gamma - alpha;
    
    % compute POI (see diagram)
    l = (p2 - p1)/norm(p2 - p1); % unit vector between mics
    cand = calcSingleCand(beta, alpha, l, p1, p2);
    candStar = calcSingleCand(-beta, -alpha, l, p1, p2);
end

function [cand] = calcSingleCand(beta, alpha, l, p1, p2)
    rotBeta = [cos(beta), -sin(beta); sin(beta), cos(beta)];
    rotAlpha = [cos(pi - alpha), -sin(pi - alpha); sin(pi - alpha), cos(pi - alpha)];
    
    v1 = rotAlpha * l;
    v2 = rotBeta * l;
    
    % solve parametric system of equations for POI
    par = [v1(1), -v2(1); v1(2), -v2(2)]^-1 * (p2 - p1); %[t, s]
    s = p1 + par(1) * v1 % or p2 + par(2)*v2;
    cand = s - (p1 + (p2 - p1)/2);
end