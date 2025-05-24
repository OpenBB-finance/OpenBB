// @ts-nocheck

export const non_blocking = (func: Function, delay: number) => {
  let timeout: number;
  return function () {
    // @ts-ignore
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
};

