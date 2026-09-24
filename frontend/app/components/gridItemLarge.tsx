// Used for the dataset page to display data about the selected dataset.
export default function GridItemLarge({ metadata }: { metadata: any }) {
  return (
    <div className="w-full shadow-lg rounded-lg p-6 border overflow-x-hidden overflow-y-scroll bg-white">
      <h2 className="text-xl font-bold underline">{metadata.title}</h2>

      <p
        style={metadata.topicStyle}
        className="flex-initial text-l max-w-fit border-medium_blue bg-blue-100 text-midnight_blue border-2 rounded my-2 px-2.5 py-0.5 font-semibold"
      >
        {metadata.topic}
      </p>

      <p className="my-1">
        <span className="font-semibold">Description: </span>
        <span>{metadata.description}</span>
      </p>

      <p className="my-1">
        <span className="font-semibold">Licenses: </span>
        <span>{metadata.licenses}</span>
      </p>

      <p className="my-1">
        <span className="font-semibold">Tags: </span>
        <span>{metadata.tags}</span>
      </p>

      <p className="font-semibold my-4 underline">
        <button
          className="bg-sas_blue hover:bf-midnight_blue text-white font-bold py-2 px-4 rounded"
          onClick={() => {
            window.open("https://" + metadata.url);
          }}
        >
          View Source
        </button>
      </p>
    </div>
  );
}
