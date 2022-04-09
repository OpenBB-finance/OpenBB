import { useState } from "react";

/**
 * Generic input form
 *
 * @class      FormInput (name)
 * @param {} arg1 Arguments
 * @param {} arg1.itemParent      The item parent
 * @param {} arg1.index           The item index
 * @param {} arg1.onChangeParent  On change parent function
 * @returns {} Gemeric input form
 */
export default function FormInput({
  itemParent,
  index,
  onChangeParent,
}: {
  itemParent: any;
  index: number;
  onChangeParent: any;
}): any {
  const [item, setItem] = useState({
    key: itemParent.key,
    value: itemParent.value,
  });
  const onChange = (event: any) => {
    const newValue =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;

    setItem((prevState) => {
      const value = item.value;
      value.value = newValue;
      const newItem = { ...prevState, value: value };
      onChangeParent(index, newItem);
      return newItem;
    });
  };
  return (
    <>
      <label className="inputFieldLabel">{item.value.title}</label>
      <input
        className={item.value.title}
        type={item.value.form}
        checked={
          item.value.form === "checkbox"
            ? item.value.value === ""
              ? item.value.default
              : item.value.value
            : false
        }
        value={item.value.value === "" ? item.value.default : item.value.value}
        onChange={onChange}
      />
    </>
  );
}
