clc; clear all;

[p1, p2, p3] = generateMicPos(1);
[d1, d2, d3] = calcIdealDelay([5; 5], p1, p2, p3);

c = zeros(2, 6); r = zeros(2, 6);
[c(:, 1), c(:, 2)] = calcCandidate(d1, d2, p1, p2);
r(:, 1) = p1 + (p2 - p1)/2;
r(:, 2) = p1 + (p2 - p1)/2;

[c(:, 3), c(:, 4)] = calcCandidate(d2, d3, p2, p3);
r(:, 3) = p2 + (p3 - p2)/2;
r(:, 4) = p2 + (p3 - p2)/2;

[c(:, 5), c(:, 6)] = calcCandidate(d1, d3, p1, p3);
r(:, 5) = p1 + (p3 - p1)/2;
r(:, 6) = p1 + (p3 - p1)/2;

maxSim = calcSimilarity(c(:, 1), c(:, 3), c(:, 5));
inds = [1, 3, 5];
for i = 1:2
    for j = 3:4
        for k = 5:6
            sim = calcSimilarity(c(:, i), c(:, j), c(:, k));
            if (sim > maxSim)
                inds = [i, j, k];
                maxSim = sim;
            end
        end
    end
end

% select candidate vectors to be used
for i = 1:3
    for j = (i+1):3
        calcPOI(r(:, inds(i)), r(:, inds(j)), c(:, inds(i)), c(:, inds(j)))
    end
end

