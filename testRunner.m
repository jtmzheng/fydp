clc; clear all;

[p1, p2, p3] = generateMicPos(1);
[d1, d2, d3] = calcIdealDelay([5; 5], p1, p2, p3);

[c1, c1s] = calcCandidate(d1, d2, p1, p2);
[c2, c2s] = calcCandidate(d2, d3, p2, p3);
[c3, c3s] = calcCandidate(d1, d3, p1, p3);