import { titleCase } from "title-case";

// Utility function to beautify text.
export const processMetadata = (dataset: any) => {
  // dataset.title = dataset.title.replace(/,/g, ", ");
  // dataset.topic = dataset.topic.replace(/,/g, ", ");
  // dataset.licenses = dataset.licenses.replace(/,/g, ", ");
  // dataset.tags = dataset.tags.replace(/,/g, ", ");
  dataset.title = titleCase(dataset.title);
  dataset.topic = titleCase(dataset.topic);
  dataset.licenses = titleCase(dataset.licenses);
  dataset.tags = titleCase(dataset.tags);
  dataset.topicStyle = hashToStyle(hashCode(dataset.topic));
  dataset.similarityStyle = scoreToStyle(dataset.score);
  return dataset;
};

export const scoreToStyle = (score: number) => {
  score = score * 100 + 50
  const hue = 2 * (score - 47.5)
  const background = `hsl(${hue}, 90%, 90%)`;
  const text = `hsl(${hue}, 50%, 20%)`;
  const border = `hsl(${hue}, 50%, 35%)`;

  const style = {
    backgroundColor: background,
    color: text,
    borderColor: border,
  };

  return style;
}

export const hashCode = (str: string) => {
  // Naive hashcode computation.
  let hash = 0;
  for (let i = 0, len = str.length; i < len; i++) {
    let chr = str.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0;
  }
  return Math.abs(hash);
};

export const hashToStyle = (hash: number) => {
  // Use hash to dynamically compute a color.
  const hue = hash % 360;
  const background = `hsl(${hue}, 50%, 90%)`;
  const text = `hsl(${hue}, 50%, 20%)`;
  const border = `hsl(${hue}, 50%, 35%)`;

  const style = {
    backgroundColor: background,
    color: text,
    borderColor: border,
  };

  return style;
};
