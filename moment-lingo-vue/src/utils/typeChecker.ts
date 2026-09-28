class TypeChecker {
  /**
   * 判断值是否为 null 或 undefined
   * @param value 要检查的值
   * @returns 如果是 null 或 undefined 则返回 true，否则返回 false
   */
  static isNullOrUndefined(value: unknown): value is null | undefined {
    return value === null || value === undefined;
  }

  /**
   * 判断值是否为非 null 且非 undefined
   * @param value 要检查的值
   * @returns 如果不是 null 且不是 undefined 则返回 true，否则返回 false
   */
  static isNotNullOrUndefined<T>(value: T): value is NonNullable<T> {
    return !this.isNullOrUndefined(value);
  }
}


export { TypeChecker };
