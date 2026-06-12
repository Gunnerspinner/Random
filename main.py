function startGame() {
   myGamePiece = new component(30, 30, "red", 10, 120);
   myGamePiece = new component(30, 30, "red", 10, 120);
   myGamePiece.gravity = 0.05;
   myGamePiece.gravity = 0.05;
   myScore = new component("30px", "Consolas", "black", 280, 40, "text");
   myScore = new component("30px", "Consolas", "black", 280, 40, "text");
 @@ -17,4 +17,4 @@
   clear : function() {
   clear : function() {
     this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
     this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
   }
   }
}</script>
}
