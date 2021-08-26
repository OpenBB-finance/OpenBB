/**
 * Text input widget containing a name label and a text input field.
 *
 * @class      TextInput (name)
 * @param root0 - s: Settings object
 * @param root0.name - s.name: Settings paramemer name (object key)
 * @param root0.value - s.value: Settings paramemer text
 * @param root0.updateFuction - Settings paramemer update fuction
 * @returns  - JSX.Element Text input component
 */
export default function TextInput({
  name,
  value,
  updateFuction,
}: {
  name: string;
  value: string;
  updateFuction: any;
}): any {
  return (
    <div className="textInput">
      <label className="settingsLabel" htmlFor="token">
        Token:
      </label>
      <br />
      <input
        type="text"
        id={`${name}-input`}
        name={name}
        value={value}
        onChange={(e) => {
          updateFuction(e.target.value);
        }}
      />
      <br />
      <br />
    </div>
  );
}
