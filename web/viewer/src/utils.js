
export const procentage = (a, b) => {
    if (b === 0)
        return 0;

    return Math.round(100 * a/b);
}
