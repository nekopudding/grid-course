/**
 * Compares two timestrings.
 * @param {string} a
 * @param {string} b
 * @returns {number} 0 if equal, -1 if a is earlier than b, 1 if a is later than b
 */
export const timeCompare = (a, b) => {
    let x = a.split(":").map(v => parseInt(v));
    let y = b.split(":").map(v => parseInt(v));
    if (x[0] === y[0]) {
        if (x[1] === y[1]) return 0;
        else if (x[1] > y[1]) return 1;
        else return -1;
    }
    else if (x[0] > y[0]) return 1;
    else return -1;
};