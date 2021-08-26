import { useState } from 'react';

/**
 * @param root0
 * @param root0.key
 * @param root0.value
 * @param root0.itemParent
 * @param root0.index
 * @param root0.onChangeParent
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
  const [item, setItem] = useState({key:itemParent.key, value:itemParent.value})
  console.log(item)
  const onChange = (event: any) => {
    const newValue = event.target.value;
    setItem((prevState) => {
      const newItem = { ...prevState, value: newValue };
      onChangeParent(index, newItem);
      return newItem;
    });
  };
  return (
    <>
      <label className="inputFieldLabel">{item.value.title}</label>
      <input type={item.value.form} value={item.value.default} onChange={onChange}/>
    </>
  );
}
