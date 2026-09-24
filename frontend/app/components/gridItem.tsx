// Component for an item in the Grid.
import Link from "next/link";
import { Tooltip as ReactTooltip } from "react-tooltip";

export default function GridItem({
  metadata,
  children,
}: {
  metadata: any;
  children?: React.ReactNode;
}) {
  return (
    <div className="w-full shadow-lg rounded-lg p-6 border overflow-x-hidden overflow-y-scroll bg-white">
      <Link href={`/dataset/${metadata.id}`}>
        <h2 className="text-xl font-bold underline">{metadata.title}</h2>
      </Link>

      <div className="flex space-x-1">
        <p
          style={metadata.topicStyle}
          className="flex-initial text-l max-w-fit border-medium_blue bg-blue-100 text-midnight_blue border-2 rounded my-2 px-2.5 py-0.5 font-semibold"
        >
          {metadata.topic}
        </p>
        {metadata.score && (
          <div className="flex flex-row justify-center text-l border-medium_blue bg-blue-100 text-midnight_blue border-2 rounded my-2 pl-2.5 pr-1 py-0.5 font-semibold"
            style={metadata.similarityStyle}>
              <p>
                {Math.round(100 * metadata.score) / 100}
              </p>
              <p data-tooltip-id={"tooltip" + metadata.id} style={{borderRadius: '50%', alignSelf: "center"}} className="text-gray-700 bg-gray-300 border-2 flex items-center rounded-full h-5 w-5 justify-center">?</p>
            <ReactTooltip
              id={"tooltip" + metadata.id}
              place="top"
              content="Similarity Score indicates how similar this dataset is to the chosen dataset. Higher = Better."
            />
          </div>
        )}
      </div>


      {children}

      <p className="my-1">
        <span className="font-semibold">Licenses: </span>
        <span>{metadata.licenses}</span>
      </p>

      <p className="my-1">
        <span className="font-semibold">Tags: </span>
        <span>{metadata.tags}</span>
      </p>
    </div>
  );
}