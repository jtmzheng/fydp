function [f] = calcSimilarity(p1, p2, p3)
    f = dot(p1, p2) + dot(p1, p3) + dot(p2, p3);
end