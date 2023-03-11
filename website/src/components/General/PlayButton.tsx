import React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog";
import PlayIcon from "../Icons/Play"
import CloseIcon from "../Icons/Close";

export default function PlayButton({ text, pathname }) {

  const pathvalue = pathname.split("/")[4];
  const platform = pathname.split("/")[3];
  var imgname = "c3m"

  // TODO - Check these - make sure they all work - So far need to do a special case for these 2
  // menus as we don't do the same thing for them as we do for the other pages
  if (pathvalue === "chart" || "general") {
    imgname = text.split(" ")[0].toLowerCase().replace("/", "");
  } else {
    try{
      imgname = text.split(" ")[1].toLowerCase().replace("/", "");
    } catch (e) {
      imgname = text.split(" ")[0].toLowerCase().replace("/", "");
    }
  }

  //console.log(platform)
  //console.log(pathvalue)
  //console.log(imgname)

  const img5 = `https://openbb-assets.s3.amazonaws.com/${platform}/${pathvalue}/${imgname}.png`;

  return (
    <DialogPrimitive.Root>
      <DialogPrimitive.Trigger className="_link-icon">
        <PlayIcon className="w-4 h-4" />
      </DialogPrimitive.Trigger>
      <DialogPrimitive.Overlay className="_modal-overlay" />
      <DialogPrimitive.Content className="_modal max-h-[50vh] p-0">
        <img className="h-full w-full" src={img5} alt={pathvalue} />
        <DialogPrimitive.Close className="absolute top-0 right-0 p-2">
          <CloseIcon className="w-4 h-4" />
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Root>
  );
}
