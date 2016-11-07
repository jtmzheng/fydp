function [theta] = calcTheta(f1, f2, l)
    init_val = [5, pi/6];
    f = @(x)delayFunc(x, f1, f2, l);
    result = fsolve(f, init_val);
    theta = radtodeg(result(2));
end