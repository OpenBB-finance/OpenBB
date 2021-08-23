/**
 * Part of [Canivete](http://canivete.leofavre.com/#deepgroupby)
 *
 * Groups the contents of an array by one or more iteratees.
 * Unlike Lodash [`groupBy()`](https://lodash.com/docs/4.17.4#groupBy),
 * this function can create nested groups, but cannot receive
 * strings for iteratees.
 */

const groupBy = (e, ...t) => {
    let r = e.map((e) => t.map((t) => t(e))),
      a = {};
    return (
      r.forEach((t, r) => {
        let l = (_simpleAt(a, t) || []).concat([e[r]]);
        _simpleSet(a, t, l);
      }),
      a
    );
  },
  _isPlainObject = (e) =>
    null != e && "object" == typeof e && e.constructor == Object,
  _parsePath = (e) => (Array.isArray(e) ? e : `${e}`.split(".")),
  _simpleAt = (e, t) =>
    _parsePath(t).reduce(
      (e, t) => (null != e && e.hasOwnProperty(t) ? e[t] : void 0),
      e
    ),
  _simpleSet = (e, t, r) =>
    _parsePath(t).reduce((e, t, a, l) => {
      let s = a === l.length - 1;
      return (
        (e.hasOwnProperty(t) && (s || _isPlainObject(e[t]))) || (e[t] = {}),
        s ? (e[t] = r) : e[t]
      );
    }, e);
