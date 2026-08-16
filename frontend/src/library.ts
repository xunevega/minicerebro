import type { KnowledgeCard } from "./types/api";

export const libraryAreas = [
  { id: "all", label: "Todo", description: "Todas las fichas publicadas." },
  { id: "gramatica", label: "Gramática", description: "Sintaxis, concordancia y estructura de frase." },
  { id: "ortografia", label: "Ortografía", description: "Tildes, signos, mayúsculas y puntuación." },
  { id: "lexico", label: "Léxico", description: "Palabra precisa, sinonimia, registro y uso." },
  { id: "estilo", label: "Estilo", description: "Claridad, ritmo, tono y párrafo." },
  { id: "retorica", label: "Retórica", description: "Argumentación, ethos, pathos, logos y discurso." },
  { id: "narrativa", label: "Narrativa", description: "Escena, voz, personaje, trama y punto de vista." },
  { id: "revision", label: "Revisión", description: "Corrección, reescritura y taller de borrador." },
] as const;

export type LibraryAreaId = (typeof libraryAreas)[number]["id"];

export type LibraryClassification = {
  area: Exclude<LibraryAreaId, "all">;
  use: string;
  level: string;
};

export const querySuggestions = [
  { id: "puntuacion", label: "Puntuación", query: "puntuación coma tilde" },
  { id: "tono", label: "Tono", query: "tono registro distancia" },
  { id: "parrafo", label: "Párrafo", query: "párrafo progresión claridad" },
  { id: "gramatica", label: "Gramática", query: "complemento sujeto concordancia" },
  { id: "lexico", label: "Léxico", query: "palabra precisa sinónimo registro" },
  { id: "revision", label: "Revisión", query: "revisión reescritura borrador" },
] as const;

export function classifyKnowledgeCard(card: KnowledgeCard): LibraryClassification {
  const text = normalizeLibraryText(`${card.name} ${card.definition} ${card.card_type}`);
  const payloadText = normalizeLibraryText(JSON.stringify(card.payload ?? {}));
  const searchableText = `${text} ${payloadText}`;

  let area: LibraryClassification["area"] = "estilo";
  if (
    containsAny(searchableText, [
      "coma",
      "punto",
      "tilde",
      "acentuacion",
      "mayuscula",
      "comillas",
      "raya",
      "cursiva",
      "sigla",
      "abreviatura",
      "versalita",
      "ortografia",
      "puntuacion",
    ])
  ) {
    area = "ortografia";
  } else if (
    containsAny(searchableText, [
      "complemento",
      "subordinada",
      "sujeto",
      "predicado",
      "atributo",
      "concordancia",
      "dequeismo",
      "queismo",
      "gramatica",
      "sintaxis",
      "lengua",
      "habla",
      "competencia linguistica",
    ])
  ) {
    area = "gramatica";
  } else if (
    containsAny(searchableText, [
      "sinon",
      "anton",
      "lexic",
      "palabra",
      "registro",
      "campo semantico",
      "familia lexica",
      "colocacion",
      "extranjerismo",
      "corpus",
      "terminologia",
      "significante",
      "significado",
    ])
  ) {
    area = "lexico";
  } else if (
    containsAny(searchableText, [
      "retorica",
      "ethos",
      "pathos",
      "logos",
      "inventio",
      "dispositio",
      "elocutio",
      "actio",
      "memoria",
      "entimema",
      "auditorio",
      "argument",
    ])
  ) {
    area = "retorica";
  } else if (
    containsAny(searchableText, [
      "narr",
      "escena",
      "personaje",
      "trama",
      "analepsis",
      "prolepsis",
      "focalizacion",
      "mimesis",
      "mythos",
      "punto de vista",
      "voz narrativa",
      "dialogo",
      "subtexto",
      "tension",
      "conflicto",
      "arco",
      "revelacion",
      "promesa",
    ])
  ) {
    area = "narrativa";
  } else if (
    containsAny(searchableText, [
      "revision",
      "reescritura",
      "correccion",
      "borrador",
      "taller",
      "cierre",
      "entrada y salida",
    ])
  ) {
    area = "revision";
  }

  return {
    area,
    use: classifyLibraryUse(searchableText, area),
    level: classifyLibraryLevel(searchableText, area),
  };
}

export function libraryAreaRank(area: LibraryAreaId) {
  return libraryAreas.findIndex((item) => item.id === area);
}

export function libraryAreaLabel(area: LibraryClassification["area"]) {
  return libraryAreas.find((item) => item.id === area)?.label ?? area;
}

function classifyLibraryUse(text: string, area: LibraryClassification["area"]) {
  if (containsAny(text, ["correccion", "coma", "tilde", "concordancia", "dequeismo", "queismo"])) {
    return "corregir";
  }
  if (containsAny(text, ["sinon", "anton", "palabra", "lexic", "matiz", "precision"])) {
    return "precisar";
  }
  if (containsAny(text, ["escena", "personaje", "trama", "narr", "dialogo"])) {
    return "narrar";
  }
  if (containsAny(text, ["retorica", "argument", "ethos", "pathos", "logos"])) {
    return "argumentar";
  }
  if (containsAny(text, ["revision", "reescritura", "borrador", "correccion de estilo"])) {
    return "revisar";
  }
  if (area === "ortografia" || area === "gramatica") {
    return "corregir";
  }
  return "aclarar";
}

function classifyLibraryLevel(text: string, area: LibraryClassification["area"]) {
  if (
    containsAny(text, [
      "generativa",
      "narratologia",
      "ortotipografia",
      "retorica",
      "formalismo",
      "estructuralismo",
      "diacronia",
      "sincronia",
    ])
  ) {
    return "avanzado";
  }
  if (
    containsAny(text, [
      "escena",
      "revision",
      "reescritura",
      "voz del autor",
      "no ficcion",
      "taller",
    ])
  ) {
    return "taller";
  }
  if (
    containsAny(text, [
      "coma",
      "sujeto",
      "predicado",
      "complemento",
      "tilde",
      "mayuscula",
      "claridad",
    ])
  ) {
    return "basico";
  }
  return area === "retorica" || area === "narrativa" ? "avanzado" : "medio";
}

function normalizeLibraryText(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function containsAny(value: string, needles: string[]) {
  return needles.some((needle) => value.includes(needle));
}
