import { describe, expect, it } from "vitest";
import { Session } from "./session";

const TEAM = ["Adeline", "Camille", "Marion", "Yoann"];

describe("Session", () => {
  it("commence avec tous les Participants Restants, sans Désigné (SE-01)", () => {
    const s = new Session(TEAM);
    expect(s.remaining).toEqual(TEAM);
    expect(s.designated).toBeNull();
    expect(s.isComplete).toBe(false);
  });

  it("retire un Participant qui a parlé, en gardant l'ordre de l'Équipe (SE-02)", () => {
    const s = new Session(TEAM);
    s.markSpoken("Camille");
    expect(s.remaining).toEqual(["Adeline", "Marion", "Yoann"]);
    expect(s.spokenCount).toBe(1);
  });

  it("refuse un nom inconnu ou déjà marqué", () => {
    const s = new Session(TEAM);
    expect(s.markSpoken("Inconnu")).toBe(false);
    expect(s.markSpoken("Marion")).toBe(true);
    expect(s.markSpoken("Marion")).toBe(false);
  });

  it("efface le Désigné au clic sur n'importe quelle Tuile (SE-03)", () => {
    const s = new Session(TEAM);
    s.draw(() => 0);
    expect(s.designated).not.toBeNull();
    s.markSpoken("Yoann");
    expect(s.designated).toBeNull();
  });

  it("ne tire jamais le Désigné actuel (SE-04)", () => {
    const s = new Session(TEAM);
    let previous = s.draw(() => 0);
    for (let i = 0; i < 50; i++) {
      const next = s.draw();
      expect(next).not.toBeNull();
      expect(next).not.toBe(previous);
      previous = next;
    }
    const s2 = new Session(["Adeline", "Camille"]);
    s2.draw(() => 0);
    expect(s2.draw()).toBe("Camille");
    expect(s2.draw()).toBe("Adeline");
  });

  it("ne tire que parmi les Restants", () => {
    const s = new Session(TEAM);
    s.markSpoken("Adeline");
    s.markSpoken("Camille");
    const drawn = new Set<string>();
    for (let i = 0; i < 50; i++) {
      const name = s.draw();
      if (name) drawn.add(name);
    }
    expect([...drawn].sort()).toEqual(["Marion", "Yoann"]);
  });

  it("désactive le Tirage quand le seul Restant est le Désigné (SE-05)", () => {
    const s = new Session(["Adeline", "Camille"]);
    s.markSpoken("Adeline");
    expect(s.canDraw).toBe(true);
    s.draw();
    expect(s.designated).toBe("Camille");
    expect(s.canDraw).toBe(false);
    expect(s.draw()).toBeNull();
  });

  it("annule d'abord le Désigné, puis les prises de parole (SE-07)", () => {
    const s = new Session(TEAM);
    s.markSpoken("Adeline");
    s.draw(() => 0);
    expect(s.undo()).toEqual({ cleared: "designated", name: s.designated ?? "Camille" });
    expect(s.designated).toBeNull();
    expect(s.undo()).toEqual({ cleared: "spoken", name: "Adeline" });
    expect(s.remaining).toEqual(TEAM);
    expect(s.undo()).toBeNull();
  });

  it("rend le Participant annulé à sa place dans l'ordre de l'Équipe (SE-07)", () => {
    const s = new Session(TEAM);
    s.markSpoken("Camille");
    s.markSpoken("Adeline");
    s.undo();
    expect(s.remaining).toEqual(["Adeline", "Marion", "Yoann"]);
  });

  it("active l'annulation dès qu'il y a un Désigné (SE-08)", () => {
    const s = new Session(TEAM);
    expect(s.canUndo).toBe(false);
    s.draw();
    expect(s.canUndo).toBe(true);
  });

  it("est complète quand tout le monde a parlé (SE-10)", () => {
    const s = new Session(TEAM);
    for (const name of TEAM) s.markSpoken(name);
    expect(s.isComplete).toBe(true);
    expect(s.remaining).toEqual([]);
    expect(s.canDraw).toBe(false);
  });
});
